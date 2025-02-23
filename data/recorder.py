import json
import csv
import sqlite3
import pymysql
import pandas as pd



class SavingOptions:
    def __init__(self) -> None:
        
        # Database save options
        self.saveToMySql = False
        self.mysqlConfig = {
            "host": "ygk-dev.ct2ame0qm97e.eu-central-1.rds.amazonaws.com",
            "user": "admin",
            "password": "ygk2024..",
            "database": "linkedin"
        }
        self.saveToSqlite = False
        self.sqliteFilePath = "./outputs/data.sqlite"

        # File save options
        self.saveToJson = False
        self.jsonFilePath = "./outputs/data.json"
        self.saveToCSV = False
        self.csvFilePath = "./outputs/data.csv"
        self.saveToExcel = False
        self.excelFilePath = "./outputs/data.xlsx"


class Recorder:
    """
        - MySQL Table Query
            CREATE TABLE company (
                id INT AUTO_INCREMENT PRIMARY KEY, -- Benzersiz ve birincil anahtar
                name VARCHAR(255) NOT NULL,        -- Şirketin adı (zorunlu)
                linkedin_url VARCHAR(255) UNIQUE,  -- Şirketin linkedin sayfası
                about TEXT,                        -- Şirket hakkında bilgi
                website VARCHAR(255) UNIQUE,       -- Benzersiz web sitesi adresi
                phoneNumber VARCHAR(20),           -- Telefon numarası
                sector VARCHAR(100),               -- Sektör bilgisi
                compSize VARCHAR(50),              -- Şirket büyüklüğü
                followerCount INT,				   -- Takipçi sayısı
                associatedMembers TEXT,            -- İlişkili üyeler (metin formatında)
                generalCenterLocation VARCHAR(255),-- Genel merkez konumu
                professions TEXT,                  -- Şirketin ilgilendiği meslekler
                country VARCHAR(50),			   -- Genel merkezin bulunduğu ülke
                location1 VARCHAR(255),            -- İlk ek konum
                location2 VARCHAR(255),            -- İkinci ek konum
                location3 VARCHAR(255)             -- Üçüncü ek konum
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    """
    
    
    def __init__(self, savingOptions: SavingOptions = SavingOptions()) -> None:
        self.savingOptions = savingOptions

    def save(self, data):
        if self.savingOptions.saveToCSV:
            self.save_to_csv(data)
        if self.savingOptions.saveToJson:
            self.save_to_json(data)
        if self.savingOptions.saveToExcel:
            self.save_to_excel(data)
        if self.savingOptions.saveToMySql:
            self.save_to_mysql(data)
        if self.savingOptions.saveToSqlite:
            self.save_to_sqlite(data)

    def save_to_csv(self, data):
        try:
            with open(self.savingOptions.csvFilePath, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"Data saved to CSV at {self.savingOptions.csvFilePath}")
        except Exception as e:
            print(f"Failed to save to CSV: {e}")

    def save_to_json(self, data):
        try:
            with open(self.savingOptions.jsonFilePath, mode='w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=4)
            print(f"Data saved to JSON at {self.savingOptions.jsonFilePath}")
        except Exception as e:
            print(f"Failed to save to JSON: {e}")

    def save_to_excel(self, data):
        try:
            df = pd.DataFrame(data)
            df.to_excel(self.savingOptions.excelFilePath, index=False)
            print(f"Data saved to Excel at {self.savingOptions.excelFilePath}")
        except Exception as e:
            print(f"Failed to save to Excel: {e}")

    def save_to_mysql(self, data):
        """
            Sample Data:
            data = {
                "id": 1,
                "name": "Tech Solutions",
                "linkedin_url": "www.linkedin.com/in"
                "about": "Software development and IT consulting.",
                "website": "https://techsolutions.com",
                "phoneNumber": "+1234567890",
                "sector": "IT",
                "compSize": "50",
                "followerCount": 50,
                "associatedMembers": "John Doe, Jane Smith",
                "generalCenterLocation": "New York, USA",
                "professions": "Software Engineer, Project Manager",
                "country": "Germany",
                "location1": "New York, USA",
                "location2": "Los Angeles, USA",
                "location3": "San Francisco, USA",
            }
        """
        
        try:
            conn = pymysql.connect(
                host=self.savingOptions.mysqlConfig["host"],
                user=self.savingOptions.mysqlConfig["user"],
                password=self.savingOptions.mysqlConfig["password"],
                database=self.savingOptions.mysqlConfig["database"],
            )
            
            cursor = conn.cursor()
            table_name = "company"
            
            # Veri ekleme
            keys = ", ".join(data.keys())
            values_placeholder = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO {table_name} ({keys}) VALUES ({values_placeholder})"
            
            cursor.execute(query, tuple(data.values()))

            conn.commit()
            conn.close()
            print("Data saved to MySQL")
        except Exception as e:
            print(f"Failed to save to MySQL: {e}")

    def save_to_sqlite(self, data):
        """
            Sample Data:
            data = {
                "id": 1,
                "name": "Tech Solutions",
                "linkedin_url": "www.linkedin.com/in"
                "about": "Software development and IT consulting.",
                "website": "https://techsolutions.com",
                "phoneNumber": "+1234567890",
                "sector": "IT",
                "compSize": "50",
                "followercount": 50,
                "associatedMembers": "John Doe, Jane Smith",
                "generalCenterLocation": "New York, USA",
                "professions": "Software Engineer, Project Manager",
                "country": "Germany",
                "location1": "New York, USA",
                "location2": "Los Angeles, USA",
                "location3": "San Francisco, USA",
            }
        """
        try:
            conn = sqlite3.connect(self.savingOptions.sqliteFilePath)
            cursor = conn.cursor()
            table_name = "company"
            
            
            # Veri ekleme
            keys = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            query = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"

            cursor.execute(query, tuple(data.values()))

            conn.commit()
            conn.close()
            print(f"Data saved to SQLite at {self.savingOptions.sqliteFilePath}")
        except Exception as e:
            print(f"Failed to save to SQLite: {e}")
