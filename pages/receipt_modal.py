from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from models import Receipt
from pages.base_page import BasePage
from utils.money import parse_amount


class ReceiptModal(BasePage):
    SUCCESS_MODAL = (By.XPATH, "//*[@id='modal-success']")
    SUCCESS_BET_ID = (By.XPATH, "//*[@id='modal-success-bet-id']")
    SUCCESS_MATCH = (By.XPATH, "//*[@id='modal-success-match']")
    # The receipt is required to show the selection. Point this at that node if the id differs.
    SUCCESS_SELECTION = (By.XPATH, "//*[@id='modal-success-selection']")
    SUCCESS_STAKE = (By.XPATH, "//*[@id='modal-success-stake']")
    SUCCESS_ODDS = (By.XPATH, "//*[@id='modal-success-odds']")
    SUCCESS_PAYOUT = (By.XPATH, "//*[@id='modal-success-payout']")
    SUCCESS_PLACED_AT = (By.XPATH, "//*[@id='modal-success-placed-at']")
    SUCCESS_CLOSE = (By.XPATH, "//*[@id='modal-success-close']")
    ERROR_MODAL = (By.XPATH, "//*[@id='modal-error']")
    ERROR_MESSAGE = (By.XPATH, "//*[@id='modal-error-message']")

    def wait_for_outcome(self) -> str:
        """Wait until placement resolves to the success receipt or the error modal."""
        try:
            self.wait.until(
                lambda driver: driver.find_elements(*self.SUCCESS_MODAL)
                or driver.find_elements(*self.ERROR_MODAL)
            )
        except TimeoutException as error:
            raise AssertionError(
                "Place Bet did not resolve to a success receipt or an error modal "
                f"within {self.wait._timeout}s"
            ) from error
        if self.present(self.ERROR_MODAL):
            return "error"
        return "success"

    def error_message(self) -> str:
        return self.text(self.ERROR_MESSAGE)

    def is_open(self) -> bool:
        return self.present(self.SUCCESS_MODAL)

    def read(self) -> Receipt:
        self.find(self.SUCCESS_MODAL)
        selection_elements = self.driver.find_elements(*self.SUCCESS_SELECTION)
        selection = selection_elements[0].text.strip() if selection_elements else ""
        return Receipt(
            bet_id=self.text(self.SUCCESS_BET_ID),
            match=" ".join(self.text(self.SUCCESS_MATCH).split()),
            selection=selection,
            stake=parse_amount(self.text(self.SUCCESS_STAKE)),
            odds=parse_amount(self.text(self.SUCCESS_ODDS)),
            potential_payout=parse_amount(self.text(self.SUCCESS_PAYOUT)),
            placed_at=self.text(self.SUCCESS_PLACED_AT),
        )

    def close(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.SUCCESS_CLOSE)).click()
        self.wait.until(EC.invisibility_of_element_located(self.SUCCESS_MODAL))
