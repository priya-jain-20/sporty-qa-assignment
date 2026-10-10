from decimal import Decimal

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.money import parse_amount


class Header(BasePage):
    BALANCE = (By.XPATH, "//*[@id='header-balance']")

    def balance(self) -> Decimal:
        return parse_amount(self.text(self.BALANCE))
