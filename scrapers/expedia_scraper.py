#!/usr/bin/python
#encoding: utf8
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from base_scraper import BaseScraper
from settings import cities
import re, time


class ExpediaScraper(BaseScraper):
    def __init__(self, mode):
        self.url = 'https://www.expedia.com/Hotels'
        self.cities = cities
        self.mode = mode
        self.currency = 'USD'
        self.source = 'expedia.com'
        self.banners = [
            './/span[contains(@class, "icon-close")]',
            './/div[@class="hero-banner-box cf"]',
        ]
        BaseScraper.__init__(self)

    def scrape_pages(self):
        _next = './/button[@class="pagination-next"]/abbr'
        elements = './/div[@id="resultsContainer"]/section/article'

        while True:
            check_element = self.presence(self.driver, elements, 10)
            self.presence(self.driver, elements, 10)
            elements = self.elements(self.driver, elements)
            self.scrape_hotels(elements)

            try:
                self.presence(self.driver, _next, 5).click()
                self.wait_for_page_to_load(check_element)
            except Exception, e:
                self.driver.quit()
                self.report()
                break

    def city_element(self):
        element = './/input[@id="hotel-destination-hlp"]'
        element = self.presence(self.driver, element, 10)
        element.send_keys(self.city)
        self.close_banner()

    def checkin_element(self):
        element = './/input[@id="hotel-checkin-hlp"]' 
        element = self.presence(self.driver, element, 10)
        element.send_keys(self.checkin.strftime('%m/%d/%Y'))

    def checkout_element(self):
        element = './/input[@id="hotel-checkout-hlp"]'
        element = self.presence(self.driver, element, 10)
        element.clear()
        element.send_keys(self.checkout.strftime('%m/%d/%Y'))

    def occupancy_element(self):
        element = './/select[contains(@class, "gcw-guests-field")]/option[contains(text(), "1 adult")]'
        element = self.visibility(self.driver, element, 10)
        element.click()

    def submit_element(self):
        element1 = './/section[@id="section-hotel-tab-hlp"]/form'
        element2 = './/button[@type="submit"]'
        element = self.visibility(self.driver, element1, 10)
        element = self.visibility(element, element2, 10)
        element.click()

    def scrape_name(self, element):
        _element = './h3'
        return self.presence(element, _element, 2).text.strip()

    def scrape_review(self, element):
        _element = './/li[contains(@class, "reviewCount")]/span'

        try:
            element = self.element(element, _element)
            element = self.driver.execute_script('return arguments[0].innerHTML', element)
            return re.findall(r'([0-9,]+)', element)[0]
        except:
            return 0

    def scrape_rating(self, element):
        _element = './/li[@class="reviewOverall"]/span'
        try:
            element = self.element(element, _element)
            element = self.driver.execute_script('return arguments[0].innerHTML', element)
            return re.findall(r'([0-9.]+)', element)[0]
        except:
            return 0

    def scrape_new_price(self, element):
        _element = './/li[@data-automation="actual-price"]/a'
        try:
            return self.element(element, _element).text.lstrip('$')
        except:
            return 0

    def scrape_old_price(self, element):
        _element = './/li[@data-automation="strike-price"]/a'
        try:
            element = self.element(element, _element).text
            return re.findall(r'([0-9,]+)', element)[0]
        except:
            return 0

    def scrape_address(self, element):
        _element = './/ul[@class="hotel-info"]/li[@class="neighborhood secondary"]'
        return self.element(element, _element).text.strip()


if __name__ == '__main__':
    try:
        mode = sys.argv[1]
    except:
        mode = ''

    ExpediaScraper(url, mode)

