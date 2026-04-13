import time
import data

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from pages import UrbanRoutesPage
from helpers import retrieve_phone_code


class TestUrbanRoutes:
    driver = None
    page = None
    code = None

    @classmethod
    def setup_class(cls):
        options = Options()
        options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})

        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)

        cls.driver.get(data.urban_routes_url)
        time.sleep(2)

        cls.page = UrbanRoutesPage(cls.driver)

    def test_01_set_route(self):
        self.page.set_route(data.address_from, data.address_to)

        value = self.driver.find_element(*self.page.from_field).get_attribute("value")
        assert data.address_from in value

    def test_02_call_taxi(self):
        self.page.click_call_taxi()
        assert self.driver.find_element(*self.page.call_taxi_button).is_displayed()

    def test_03_select_comfort(self):
        self.page.select_comfort()
        assert self.driver.find_element(*self.page.comfort_rate).is_displayed()

    def test_04_set_phone(self):
        self.page.set_phone_number(data.phone_number)

        value = self.driver.find_element(*self.page.phone_input).get_attribute("value")
        assert "123" in value

    def test_05_confirm_phone(self):
        self.__class__.code = retrieve_phone_code(self.driver)

        self.page.enter_phone_code(self.code)
        self.page.confirm_phone()

        payment = self.driver.find_element(*self.page.payment_method)
        assert payment.is_displayed()

    def test_06_payment_and_extras(self):
        self.page.add_card(data.card_number, data.card_code)
        self.page.add_comment(data.message_for_driver)

        comment = self.driver.find_element(*self.page.comment_input)
        assert comment.get_attribute("value") == data.message_for_driver

        self.page.select_extras()
        self.page.add_icecream(2)

        checkbox = self.driver.find_element(*self.page.extras_checkbox)
        assert checkbox.is_selected()

    def test_07_order(self):
        self.page.click_order_button()

        self.page.wait_for_order_completion()

        element = self.driver.find_element(
            By.XPATH, "//div[contains(text(),'El conductor llegará')]"
        )
        assert element.is_displayed()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()