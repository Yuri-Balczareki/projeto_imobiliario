import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self):
        self.wait_time = 0.5
        self.initial_pos = 0
        self.last_pos = None
        self.results = []
        self.links = []

    def scrape_data(self, filename):
        # sourcery skip: extract-method, hoist-similar-statement-from-if
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            links = [row['Links'] for row in reader]

        for link in links[self.initial_pos:self.last_pos]:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.get(str(link))
            driver.maximize_window()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(self.wait_time)

        if "Você está vendo esta página porque o imóvel que buscava foi alugado ou está indisponível." in soup.get_text():
            self.initial_pos += 1
        else:
            time.sleep(self.wait_time)
            title = self.extract_content(soup, 'h1', 'title__title js-title-view')
            complete_address = self.extract_content(soup, 'p', 'title__address js-address')
            area = self.extract_content(soup, 'li', 'features__item features__item--area js-area')
            rooms = self.extract_content(soup, 'li', 'features__item features__item--bedroom js-bedrooms')
            baths = self.extract_content(soup, 'li', 'features__item features__item--bathroom js-bathrooms')
            garage = self.extract_content(soup, 'li', 'features__item features__item--parking js-parking')
            price_sale = self.extract_content(soup, 'h3', 'price__price-info js-price-sale')
            condominium_fee = self.extract_content(soup, 'span', 'price__list-value condominium js-condominium')
            iptu = self.extract_content(soup, 'span', 'price__list-value iptu js-iptu')
            ad_description = self.extract_content(soup, 'p', 'description__text')
            characteristics = self.extract_characteristics(driver)

            # Splitting the address
            add_list = re.split(',|-', complete_address)
            add_list = [item.strip() for item in add_list]
            city, state, neibhood, address, number = "N/I", "N/I", "N/I", "N/I", "N/I"

            if len(add_list) == 2:
                city, state = add_list
            elif len(add_list) == 3:
                neibhood, city, state = add_list
            elif len(add_list) == 4:
                address, neibhood, city, state = add_list
            elif len(add_list) == 5:
                address, number, neibhood, city, state = add_list

            row = {'Título': title, 'Descrição': ad_description, 'Endereço': address, 'Número': number,
                'Bairro': neibhood, 'Cidade': city, 'Estado': state, 'Área': area, 'Quartos': rooms,
                'Banheiros': baths, 'Vagas': garage, 'Preço': price_sale, 'Condomínio': condominium_fee,
                'IPTU': iptu, 'Características': characteristics, 'Link': link}
            self.results.append(row)
            self.initial_pos += 1
        driver.quit()

    def extract_content(self, soup, tag, class_name):
        try:
            content = soup.find(tag, class_name).get_text().strip()
        except AttributeError:
            content = "N/I"
        return content

    def extract_characteristics(self, driver):
        try:
            button_charac = driver.find_element(by=By.CLASS_NAME, value='js-amenities-button')
            ActionChains(driver).move_to_element(button_charac).perform()
            attempts = 0
            while attempts < 1:
                try:
                    button_charac.click()
                    time.sleep(self.wait_time)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    characteristics = soup.find('ul', 'amenities__list').get_text().strip()
                    break
                except StaleElementReferenceException as exception:
                    characteristics = "N/I"
        except ElementClickInterceptedException as exception:
            characteristics = "N/I"
        except NoSuchElementException:
            characteristics = "N/I"
        return characteristics


if __name__ == "__main__":
    scraper = WebScraper()
    scraper.scrape_data("links_sales_florianopolis.csv")
    print(scraper.results)
