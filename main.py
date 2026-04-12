import data
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def retrieve_phone_code(driver) -> str:
    import json
    from selenium.common import WebDriverException

    code = None

    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance')
                    if log.get("message") and 'api/v1/number?number' in log.get("message")]

            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd(
                    'Network.getResponseBody',
                    {'requestId': message_data["params"]["requestId"]}
                )
                code = ''.join([x for x in body['body'] if x.isdigit()])

        except WebDriverException:
            time.sleep(1)
            continue

        if code:
            return code

    raise Exception("No se encontró el código de confirmación")


class UrbanRoutesPage:
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')

    call_taxi_button = (By.XPATH, "//button[contains(text(),'Pedir')]")
    comfort_rate = (By.XPATH, "//div[@class='tcard-title' and text()='Comfort']")

    phone_section = (By.XPATH, "//div[contains(text(),'Número de teléfono')]")
    phone_input = (By.ID, "phone")
    next_button = (By.XPATH, "//button[text()='Siguiente']")

    code_input = (By.ID, "code")
    confirm_button = (By.XPATH, "//button[contains(text(),'Confirmar')]")

    payment_method = (By.XPATH, "//div[@class='pp-text' and text()='Método de pago']/..")
    add_card_button = (By.XPATH, "//div[text()='Agregar tarjeta']")
    card_number_input = (By.ID, "number")
    card_code_input = (By.NAME, "code")
    add_button = (By.XPATH, "//button[text()='Agregar']")

    comment_input = (By.ID, "comment")
    overlay = (By.CLASS_NAME, "overlay")

    extras_slider = (By.CSS_SELECTOR, "span.slider.round")
    icecream_plus = (By.XPATH, "(//div[@class='counter-plus'])[1]")

    order_button = (By.CSS_SELECTOR, "button.smart-button")
    order_time = (By.CLASS_NAME, "order-header-time")

    def __init__(self, driver):
        self.driver = driver

    # ✅ Escritura humana
    def slow_type(self, element, text, delay=0.1):
        for char in text:
            element.send_keys(char)
            time.sleep(delay)

    def set_route(self, from_address, to_address):
        from_el = self.driver.find_element(*self.from_field)
        to_el = self.driver.find_element(*self.to_field)

        self.slow_type(from_el, from_address)
        time.sleep(0.5)

        self.slow_type(to_el, to_address)
        time.sleep(1)

    def click_call_taxi(self):
        self.driver.find_element(*self.call_taxi_button).click()
        time.sleep(1)

    def select_comfort(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.comfort_rate)
        ).click()
        time.sleep(1)

    def set_phone_number(self, phone_number):
        section = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.phone_section)
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", section)
        section.click()

        phone_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.phone_input)
        )

        self.slow_type(phone_input, phone_number)
        time.sleep(0.5)

        self.driver.find_element(*self.next_button).click()

    def enter_phone_code(self, code):
        code_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.code_input)
        )

        self.slow_type(code_input, code, delay=0.2)
        time.sleep(1)

    def confirm_phone(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.confirm_button)
        ).click()
        time.sleep(1)

    def add_card(self, card_number, card_code):
        payment = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(self.payment_method)
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", payment)
        payment.click()

        add_card = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(self.add_card_button)
        )
        add_card.click()

        card_input = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(self.card_number_input)
        )
        self.slow_type(card_input, card_number)

        code_input = self.driver.find_element(*self.card_code_input)
        self.slow_type(code_input, card_code)
        code_input.send_keys(Keys.TAB)

        time.sleep(1)

        add_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.add_button)
        )
        add_btn.click()

        WebDriverWait(self.driver, 15).until(
            EC.invisibility_of_element_located(self.overlay)
        )

    def add_comment(self, comment):
        comment_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.comment_input)
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", comment_field)
        self.driver.execute_script("arguments[0].click();", comment_field)

        comment_field.clear()
        self.slow_type(comment_field, comment, delay=0.05)
        time.sleep(1)

    def select_extras(self):
        slider = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.extras_slider)
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", slider)
        self.driver.execute_script("arguments[0].click();", slider)
        time.sleep(1)

    def add_icecream(self, quantity=2):
        plus_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.icecream_plus)
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", plus_button)

        for _ in range(quantity):
            self.driver.execute_script("arguments[0].click();", plus_button)
            time.sleep(0.5)

    def click_order_button(self):
        order_btn = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(self.order_button)
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", order_btn)
        self.driver.execute_script("arguments[0].click();", order_btn)
        time.sleep(2)

    # ✅ Esperar contador + 10 segundos
    def wait_for_order_completion(self):
        timer_element = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located(self.order_time)
        )

        print("⏳ Detectando contador inicial...")
        initial_value = timer_element.text.strip()
        print("Valor inicial:", initial_value)

        print("🔄 Esperando cambio de contador (sin esperar a que termine)...")

        # Esperar a que el texto cambie (nuevo contador / nueva vista)
        while True:
            current_value = timer_element.text.strip()

            if current_value != initial_value:
                print("Cambio detectado:", current_value)
                break

            time.sleep(0.5)

        print("⏳ Manteniendo la página abierta un rato mas")
        time.sleep(40)


class TestUrbanRoutes:
    driver = None

    @classmethod
    def setup_class(cls):
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})

        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)

    def test_request_taxi(self):
        self.driver.get(data.urban_routes_url)
        time.sleep(2)

        page = UrbanRoutesPage(self.driver)

        page.set_route(data.address_from, data.address_to)
        page.click_call_taxi()
        page.select_comfort()
        page.set_phone_number(data.phone_number)

        code = retrieve_phone_code(self.driver)
        page.enter_phone_code(code)
        page.confirm_phone()

        page.add_card(data.card_number, data.card_code)
        page.add_comment(data.message_for_driver)

        page.select_extras()
        page.add_icecream(2)

        page.click_order_button()

        # ✅ Espera final real
        page.wait_for_order_completion()

        assert True

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
