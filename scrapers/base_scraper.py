import pyodbc, time, datetime, sys, traceback, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import dates, cities
from datetime import datetime, timedelta

class BaseScraper(object):
    def __init__(self, url, spider_name):
        self.spider_name = spider_name
        self.url = url
        self.dates = dates
        self.cities = cities
        self.conn, self.cur = self.sql_connect()

    def firefox(self):
        driver = webdriver.Firefox()
        driver.maximize_window()
        driver.get(self.url)
        return driver

    def chrome(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(self.url)
        return driver

    def chrome_long_window(self):
        driver = webdriver.Chrome()
        driver.set_window_size(2000, 3000)
        driver.get(self.url)
        return driver

    def base_func(self):
        for date in self.dates:
            self.date = date
            self.checkin, self.checkin2 = self.get_checkin()
            self.checkout, self.checkout2 = self.get_checkout()

            for city in self.cities:
                self.city, self.city2 = self.get_city(city)
                self.count = 0

                if self.spider_name == 'chrome':
                    self.driver = self.chrome()
                elif self.spider_name == 'firefox':
                    self.driver = self.firefox()
                elif self.spider_name == 'chrome_long_window':
                    self.driver = self.chrome_long_window()
                else:
                    pass

                self.main_page()

                self.driver.quit()

        self.conn.close()

    def get_city(self, city):
        return city, city.split(',')[0].replace("'", "''")

    def presence(self, driver, element, delay):
        return WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, element)))

    def visibility(self, driver, element, delay):
        return WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.XPATH, element)))

    def clickable(self, driver, element):
        for x in range(50):
            try:
                self.element(self.driver, element).click()
                break
            except:
                time.sleep(0.2)

    def elements(self, driver, elements):
        return driver.find_elements_by_xpath(elements)

    def element(self, driver, element):
        return driver.find_element_by_xpath(element)

    def click_elements(self, elements):
        elements = self.elements(self.driver, elements)
        time.sleep(2)
        for element in elements:
            try:
                element.click()
                break
            except Exception, e:
                time.sleep(1)

    def wait_for_page_to_load(self, element):
        while True:
            try:
                self.element(element, './/a')
                time.sleep(0.2)
            except:
                break

        return 0

    def wait_for_window(self, delay):
        WebDriverWait(self.driver, delay).until(lambda x: len(self.driver.window_handles) > 1)

    def switch_windows(self, delay, number):
        self.wait_for_window(delay)
        self.driver.close()
        self.driver.switch_to_window(self.driver.window_handles[number])

    def get_checkin(self):
        checkin = datetime.now() + timedelta(self.date)
        checkin2 = checkin.strftime('%m/%d/%Y')
        return checkin, checkin2

    def get_checkout(self):
        checkout = datetime.now() + timedelta(self.date) + timedelta(3)
        checkout2 = checkout.strftime('%m/%d/%Y')
        return checkout, checkout2

    def sql_connect(self):
        conn = pyodbc.connect(r'DRIVER={SQL Server};SERVER=(local);DATABASE=hotels;Trusted_Connection=Yes;')
        cur = conn.cursor()
        return conn, cur

    def sql_write(self):
        name = self.name.replace("'", "''")
        address = self.address.replace("'", "''").decode('utf8')
        date_scraped = datetime.now().strftime('%m/%d/%Y')

        sql = "insert into hotel_info (hotel_name, hotel_rating, hotel_review, hotel_address,\
            new_price, old_price, checkin, checkout, city, currency, source, date_scraped,\
            hotel_position, date_range) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',\
            '%s', '%s', '%s', '%s', '%s', %s)"
            
        try:
            self.cur.execute(sql % (name, self.rating, self.review, address, self.new_price, self.old_price,\
                self.checkin2, self.checkout2, self.city2, self.currency, self.source, date_scraped, self.count, self.date))
            self.conn.commit()
        except Exception, e:
#            traceback.print_exc()           
            pass

    def report(self):
        print "{}, {}, {} hotels, checkin {}, checkout {}, range {}".format(
            self.source, 
            self.city2, 
            self.count, 
            self.checkin2, 
            self.checkout2, 
            self.date
        )

    def full_report(self):
        print """{},{},{},{},{},{},{},{},"{}",{},{},{},{}\n""".format(
            self.name.encode('utf8'), self.rating, self.review, self.new_price, self.old_price, self.checkin2,\
            self.checkout2, self.city2, self.address.encode('utf8'), self.currency, self.source, self.count, self.date
        )

    def close_banner(self):
        for banner in self.banners:
            try:
                self.visibility(self.driver, banner, 2).click()
            except:
                pass

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_click(self, element, _range, delay):
        for x in range(_range):
            try:
                self.element(self.driver, element).click()
                break
            except:
                self.element(self.driver, './/body').send_keys(Keys.ARROW_DOWN)
                time.sleep(delay)

            if x == _range - 1:
                raise ValueError()

    def scroll_to_element(self, _range, element):
        for x in range(_range):
            try:
                self.element(self.driver, element)
                break
            except:
                self.element(self.driver, './/body').send_keys(Keys.ARROW_DOWN)
                time.sleep(0.2)

    def scroll_range(self, _range):
        for x in range(_range):
            self.element(self.driver, './/body').send_keys(Keys.ARROW_DOWN)
            time.sleep(0.4)

    def scrape_hotels(self, elements):
        self.presence(self.driver, elements, 10)
        elements = self.elements(self.driver, elements)

        for element in elements:
            self.count += 1
            self.name = self.scrape_name(element)
            self.new_price = self.scrape_new_price(element)
            self.old_price = self.scrape_old_price(element)
            self.review = self.scrape_review(element)
            self.rating = self.scrape_rating(element)
            self.address = self.scrape_address(element)
            self.sql_write()
#            self.full_report()

        return 0


