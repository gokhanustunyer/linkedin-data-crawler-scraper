from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from data.dbm_helper import DBMHelper
from constants import email, password, loginUrl
from selenium.webdriver import Keys, ActionChains
import time
from urllib.parse import urlparse, urljoin
from data.recorder import Recorder, SavingOptions
import re
import csv
import pandas as pd

class LinkedinCrawler:
    
    BASE_URL = "https://www.linkedin.com"
    
    def __init__(self) -> None:
        self.driver: webdriver.Chrome = None
        self.isLoggedIn = False
        
        self.savingOptions = SavingOptions()
        self.savingOptions.saveToMySql = True
        
        self.world_cities_df = pd.read_csv('./worldcities.csv')
        self.used_urls = self.read_urls("./company_urls.csv")
        
        self.recorder = Recorder(self.savingOptions)
        
        
    def read_urls(self, fileName: str):
        with open(fileName, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return set([row[0] for row in reader])
    
    def logIntoAccount(self, email, password, headless_driver = True) -> None:
        if self.driver == None:
            self.driver = LinkedinCrawler.get_driver(headless_driver)
            
        self.driver.get(loginUrl)
        email_input = self.driver.find_element(By.ID, "username")
        password_input = self.driver.find_element(By.ID, "password")
        
        ActionChains(self.driver).send_keys_to_element(email_input, email).perform()
        ActionChains(self.driver).send_keys_to_element(password_input, password).perform()
        self.driver.find_element(By.CSS_SELECTOR, 'button[data-litms-control-urn="login-submit"]').click()
        time.sleep(5)

        self.isLoggedIn = True
        


    def start_crawling(self, start_url, headless_driver = True) -> None:
        if start_url in self.used_urls: return
        
        if self.driver == None:
            self.driver = LinkedinCrawler.get_driver(headless_driver)
            
        if not self.isLoggedIn:
            self.logIntoAccount(email, password, headless_driver)
        
        if DBMHelper.is_visited(start_url): return
        
        self.driver.get(start_url)
        source = BeautifulSoup(self.driver.page_source, 'html.parser')
       
        target_company_name = urlparse(start_url).path.strip('/').split('/')[1]

        print('SCRAPING: ', target_company_name)

        
        about_section = source.find('section', {'class': 'org-page-details-module__card-spacing'})
        about_summary = re.sub(r'\s+', ' ', about_section.getText()).strip()
        
        about_comp = self.parse_company_info(about_section)

        country = None
        
        generalCenter = about_comp["Genel Merkez"] if "Genel Merkez" in about_comp.keys() else ""
        if generalCenter == "":
            generalCenter = source.find_all('div', {'class':'org-top-card-summary-info-list__info-item'})[1].getText().strip()
        
        country_row = self.world_cities_df[self.world_cities_df["city"].str.contains(generalCenter.split(',')[0], case=False, na=False)]
        if not country_row.empty:
            country = country_row["country"].iloc[0]

        if country == None:
            if len(generalCenter.split(',')) > 1:
                country_row = self.world_cities_df[self.world_cities_df["city"].str.contains(generalCenter.split(',')[1], case=False, na=False)]
                if not country_row.empty:
                        country = country_row["country"].iloc[0]

        name = source.find('h1').getText().strip()
        sector = source.find('div', {'class':'org-top-card-summary-info-list__info-item'}).getText().strip()
        
        follower_num_str = source.find_all('div', {'class':'org-top-card-summary-info-list__info-item'})[2].getText().strip().replace(' takipçi', '')
        if "bin" in follower_num_str:
            followersCount = float(follower_num_str.replace(" bin", "")) * 1000
        elif "milyon" in follower_num_str:
            followersCount = float(follower_num_str.replace(" milyon", "")) * 1000000
        else:
            followersCount = float(follower_num_str)
            
        data = {
            "name": name,
            "linkedin_url": start_url,
            "about": about_summary,
            "website": about_comp["Web Sitesi"] if "Web Sitesi" in about_comp.keys() else "",
            "phoneNumber": about_comp["Telefon"] if "Telefon" in about_comp.keys() else "",
            "sector": sector,
            "compSize": about_comp["Şirket büyüklüğü"] if "Şirket büyüklüğü" in about_comp.keys() else "",
            "followerCount": followersCount,
            "associatedMembers": about_comp["İlişkili Üye"] if "İlişkili Üye" in about_comp.keys() else "",
            "generalCenterLocation": about_comp["Genel Merkez"] if "Genel Merkez" in about_comp.keys() else "",
            "professions": about_comp["Uzmanlık Alanları"] if "Uzmanlık Alanları" in about_comp.keys() else "",
            "country": country,
            "location1": "",
            "location2": "",
            "location3": "",
        }
        
        self.recorder.save(data)
        DBMHelper.mark_as_visited(start_url, data)
        self.used_urls.add(start_url)
 
        
        company_links = []
        time.sleep(0.35)
        self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Tüm benzer sayfaları göster"]').click()
        time.sleep(0.25)
        
        source = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        for link in source.find_all('a', href=True):
            parsed_link = urlparse(link['href']).path.strip('/').split('/')
            if 'company' in parsed_link:
                if parsed_link[1] != target_company_name:
                    next_link = link['href'] + 'about/'
                    if (not DBMHelper.is_visited(next_link)) and (next_link not in company_links):
                        company_links.append(next_link)

        for link in company_links:
            try:
                self.start_crawling(link)
            except Exception as ex:
                print("failed while scraping", link, ex)

    def parse_company_info(self, section_content):
        dl = section_content.find('dl')
        
        company_info = {}
        if dl:
            dt_elements = dl.find_all('dt')
            
            for dt in dt_elements:
                h3 = dt.find('h3', class_='text-heading-medium')
                if h3:
                    key = h3.get_text(strip=True).split('\n')[0]

                    dd = dt.find_next('dd')
                    if dd:
                        link = dd.find('a')
                        if link and link.get('href'):
                            value = link.get_text(strip=True)
                        else:
                            value = dd.get_text(strip=True)
                        
                        if "çalışan" in value:
                            match = re.match(r'\d+', dd.find_next('dd').find('a').get_text(strip=True))
                            company_info["İlişkili Üye"] = match.group()
                        
                        if 'Telefon numarası' in value:
                            value = value.split("Telefon numarası")[0]
                                
                        company_info[key] = value
                    
        return company_info

    @staticmethod
    def get_driver(headless = True) -> webdriver.Chrome:
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("--disable-gpu")
        if headless: driver_options.add_argument('--headless')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=driver_options)
        driver.maximize_window()
        return driver
