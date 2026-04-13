import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

    # CONTENEDOR SCROLL
    extras_container = (By.CLASS_NAME, "modal")

    extras_slider = (By.CSS_SELECTOR, "span.slider.round")
    extras_checkbox = (By.CSS_SELECTOR, "input.switch-input")

    icecream_plus = (By.XPATH, "(//div[@class='counter-plus'])[1]")

    order_button = (By.CSS_SELECTOR, "button.smart-button")
    order_time = (By.CLASS_NAME, "order-header-time")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    #SCROLL DE EXTRAS
    def scroll_inside_container(self, container_locator, element_locator):
        container = self.wait.until(EC.presence_of_element_located(container_locator))
        element = self.wait.until(EC.presence_of_element_located(element_locator))

        self.driver.execute_script("""
            arguments[0].scrollTop = arguments[1].offsetTop - arguments[0].offsetTop;
        """, container, element)

        time.sleep(1)
        return element

    def wait_overlay_disappear(self):
        self.wait.until(EC.invisibility_of_element_located(self.overlay))

    def slow_type(self, element, text, delay=0.1):
        for char in text:
            element.send_keys(char)
            time.sleep(delay)

    def set_route(self, from_address, to_address):
        from_el = self.driver.find_element(*self.from_field)
        to_el = self.driver.find_element(*self.to_field)

        from_el.clear()
        self.slow_type(from_el, from_address)

        to_el.clear()
        self.slow_type(to_el, to_address)

    def click_call_taxi(self):
        self.wait_overlay_disappear()
        self.driver.find_element(*self.call_taxi_button).click()

    def select_comfort(self):
        self.wait_overlay_disappear()
        self.wait.until(EC.element_to_be_clickable(self.comfort_rate)).click()

    def set_phone_number(self, phone_number):
        section = self.wait.until(EC.presence_of_element_located(self.phone_section))
        section.click()

        phone_input = self.wait.until(EC.visibility_of_element_located(self.phone_input))
        phone_input.clear()
        self.slow_type(phone_input, phone_number)

        self.driver.find_element(*self.next_button).click()

    def enter_phone_code(self, code):
        code_input = self.wait.until(EC.visibility_of_element_located(self.code_input))
        self.slow_type(code_input, code, delay=0.2)

    def confirm_phone(self):
        self.wait.until(EC.element_to_be_clickable(self.confirm_button)).click()

    def add_card(self, card_number, card_code):
        self.wait_overlay_disappear()

        payment = self.wait.until(EC.element_to_be_clickable(self.payment_method))
        payment.click()

        self.wait.until(EC.element_to_be_clickable(self.add_card_button)).click()

        card_input = self.wait.until(EC.visibility_of_element_located(self.card_number_input))
        self.slow_type(card_input, card_number)

        code_input = self.driver.find_element(*self.card_code_input)
        self.slow_type(code_input, card_code)
        code_input.send_keys(Keys.TAB)

        self.wait.until(EC.element_to_be_clickable(self.add_button)).click()

        self.wait_overlay_disappear()

    def add_comment(self, comment):
        field = self.wait.until(EC.visibility_of_element_located(self.comment_input))
        field.clear()
        self.slow_type(field, comment, delay=0.05)

    def select_extras(self):
        self.wait_overlay_disappear()

        slider = self.scroll_inside_container(self.extras_container, self.extras_slider)
        self.driver.execute_script("arguments[0].click();", slider)

    def add_icecream(self, quantity=2):
        # SCROLL A HELADOS (debajo de pañales y manta)
        plus = self.scroll_inside_container(self.extras_container, self.icecream_plus)

        self.wait.until(EC.visibility_of(plus))

        for i in range(quantity):
            plus.click()
            print(f" Helado agregado: {i + 1}")
            time.sleep(0.7)

    def click_order_button(self):
        self.wait_overlay_disappear()

        btn = self.wait.until(EC.element_to_be_clickable(self.order_button))
        self.driver.execute_script("arguments[0].click();", btn)
    #ETAPA FINAL: VALIDANDO ENCONTRAR EL CONDUCTOR:
    def wait_for_order_completion(self):
        print("Esperando búsqueda de conductor...")

        wait = WebDriverWait(self.driver, 60)

        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(text(),'Buscar automóvil')]")
            )
        )

        timer = wait.until(EC.visibility_of_element_located(self.order_time))
        initial_value = timer.text
        print("Contador inicial:", initial_value)

        print("Esperando cambio de contador...")
        wait.until(lambda d: d.find_element(*self.order_time).text != initial_value)

        print("Esperando conductor...")
        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(text(),'El conductor llegará')]")
            )
        )

        print("Conductor encontrado, esperando 10s finales...")
        time.sleep(10)