"""Shared explicit waits. Pages do not use implicit waits."""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import PAGE_TIMEOUT_SECONDS


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = PAGE_TIMEOUT_SECONDS) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def find(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def text(self, locator: tuple[str, str]) -> str:
        return self.find(locator).text.strip()

    def present(self, locator: tuple[str, str]) -> bool:
        return bool(self.driver.find_elements(*locator))

    def set_input_value(self, locator: tuple[str, str], value: str) -> None:
        """Set a React controlled input and fire the input event the slip listens for."""
        element = self.find(locator)
        self.driver.execute_script(
            """
            const element = arguments[0];
            const value = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype,
                "value"
            ).set;
            setter.call(element, value);
            element.dispatchEvent(new Event("input", { bubbles: true }));
            element.dispatchEvent(new Event("change", { bubbles: true }));
            """,
            element,
            value,
        )
