"""Desktop single-bet screen. Compose the header, match list, slip, and receipt."""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_URL, PAGE_TIMEOUT_SECONDS, PLACEMENT_TIMEOUT_SECONDS, USER_ID
from pages.base_page import BasePage
from pages.bet_slip import BetSlip
from pages.header import Header
from pages.match_list import MatchList
from pages.receipt_modal import ReceiptModal


class BettingPage(BasePage):
    def __init__(
        self,
        driver: WebDriver,
        base_url: str = BASE_URL,
        user_id: str = USER_ID,
    ) -> None:
        super().__init__(driver)
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self.header = Header(driver)
        self.matches = MatchList(driver)
        self.slip = BetSlip(driver)
        self.receipt = ReceiptModal(driver)
        # Placement waits longer than a normal page find because the button stays on Placing...
        self.receipt.wait = WebDriverWait(driver, PLACEMENT_TIMEOUT_SECONDS)

    def open(self) -> None:
        self.driver.get(f"{self.base_url}/?user-id={self.user_id}")
        self.wait_until_ready()

    def refresh(self) -> None:
        self.driver.refresh()
        self.wait_until_ready()

    def wait_until_ready(self) -> None:
        self.wait.until(lambda driver: "€" in driver.find_element(*Header.BALANCE).text)
        self.matches.wait_until_loaded()
        self.find(BetSlip.ROOT)
        # Keep the default page timeout on the sections that are not waiting for placement.
        self.header.wait = WebDriverWait(self.driver, PAGE_TIMEOUT_SECONDS)
        self.matches.wait = WebDriverWait(self.driver, PAGE_TIMEOUT_SECONDS)
        self.slip.wait = WebDriverWait(self.driver, PAGE_TIMEOUT_SECONDS)
