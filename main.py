from crawler.crawler import LinkedinCrawler
from bs4 import BeautifulSoup
import concurrent.futures
from datetime import datetime

target_urls = [
    "https://www.linkedin.com/company/safeguard-globl/about/",
    "https://www.linkedin.com/company/yedaskurumsal/about/",
    "https://www.linkedin.com/company/spyke-games/about/"
]

def spawn_crawler(start_url):
    crawler = LinkedinCrawler()
    crawler.start_crawling(
        start_url=start_url,
        headless_driver=False
    )

def main():
    crawler = LinkedinCrawler()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(spawn_crawler, target_urls)

if __name__ == '__main__':
    main()