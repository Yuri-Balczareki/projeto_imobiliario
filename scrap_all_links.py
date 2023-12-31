import numpy as np
import time 

import argparse
import os 
import pandas as pd
import csv
from bs4 import BeautifulSoup
# Manipulação com o Selenium,
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# Necessário para iniciar o Chrome.
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class RentScraper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service,  options=self.options)
        self.driver.maximize_window() 
        
    def accept_cookies(self):
        wait_time = 5
        WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cookie-notifier-cta"]'))).click()
        time.sleep(wait_time / 2)
    
    def scrape_links(self, url, wait_time=5):
        self.driver.get(url)
        time.sleep(wait_time)
        self.accept_cookies()
        
        links_rent_florianopolis = []
        repeated_links = 0
        has_next_page = True
        page_number = 0
        report = []
        
        while has_next_page:
            results_page = []
            try:
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            except WebDriverException:
                print("Webdriver was closed")

            elements_rent_florianopolis = soup.find_all('a', {'class': 'property-card__content-link js-card-title'})
            
            for element in elements_rent_florianopolis:
                link_href = element.get('href')
                full_link = "https://www.vivareal.com.br" + link_href
                if full_link not in links_rent_florianopolis:
                    links_rent_florianopolis.append(full_link)
                    results_page.append(full_link)
                else:
                    repeated_links += 1

            page_number += 1
            try:
                next_page_button = self.driver.find_element(By.XPATH, '//*[@id="js-site-main"]/div[2]/div[1]/section/div[2]/div[2]/div/ul/li[9]/button')
                ActionChains(self.driver).move_to_element(next_page_button).perform()
                
                attempts = 0
                while attempts < 2:
                    try:
                        next_page_button.click()
                        time.sleep(wait_time)
                        break
                    except StaleElementReferenceException as exception:
                        print(exception.msg)
                    attempts += 1

            except ElementClickInterceptedException:
                print("Next page element is not clickable")
                has_next_page = False
            except NoSuchElementException:
                print("Next page element was not found")
                has_next_page = False
            except AttributeError:
                has_next_page = False

            report_msg = f'Page number {page_number}. Got {len(results_page)} Results in that page. Total Found until now: {len(links_rent_florianopolis)}. Total repeated links {repeated_links}'

            print(report_msg)
            report.append(report_msg)
        
        return links_rent_florianopolis, report

    def close(self):
        self.driver.quit()

    def save_links_to_csv(self, links, filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for link in links:
                writer.writerow([link])

    def save_report_to_csv(self, report, filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for entry in report:
                writer.writerow([entry])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape rental/sales property links.")
    parser.add_argument("--url", type=str, help="The URL to scrape property links from.")
    parser.add_argument("--filename", type=str, help="The name of the CSV file to save the links.")
    args = parser.parse_args()

    # Creating the directory if it doesn't exist
    data_dir = "data/links"
    os.makedirs(data_dir, exist_ok=True)

    # Constructing the full CSV file path
    csv_path = os.path.join(data_dir, args.filename + ".csv")

    scraper = RentScraper()
    links, report = scraper.scrape_links(args.url)
    scraper.close()

    scraper.save_links_to_csv(links, csv_path)
    scraper.save_report_to_csv(report, os.path.join(data_dir, "report.csv"))

    print(f"Links saved to {csv_path}")