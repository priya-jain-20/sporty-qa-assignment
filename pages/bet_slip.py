from decimal import Decimal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from model import SlipState
from pages.base_page import BasePage
from utils.money import parse_amount


class BetSlip(BasePage):
    ROOT = (By.XPATH, "//*[@id='bet-slip']")
    COUNT = (By.XPATH, "//*[@id='bet-slip-count']")
    EMPTY = (By.XPATH, "//*[@id='bet-slip']//*[contains(@class,'betSlipBodyEmpty')]")
    TEAMS = (By.XPATH, "//*[@id='bet-slip']//*[contains(@class,'betSelectionTeams')]")
    MARKET = (By.XPATH, "//*[@id='bet-slip']//*[contains(@class,'betSelectionMarket')]")
    ODDS = (By.XPATH, "//*[@id='bet-slip']//*[contains(@class,'betSelectionOdds')]")
    STAKE_INPUT = (By.XPATH, "//*[@id='bet-slip-stake-input']")
    TOTAL_STAKE = (By.XPATH, "//*[@id='bet-slip-total-stake']")
    POTENTIAL_PAYOUT = (By.XPATH, "//*[@id='bet-slip-potential-payout']")
    PLACE_BET = (By.XPATH, "//*[@id='bet-slip-place-bet']")

    HOME = "Home"
    MATCH_WINNER_PREFIX = "Match Winner: "
    ODDS_PREFIX = "Odds: "
    EMPTY_SLIP = "Select odds to place a bet"
    PLACING = "Placing..."

    def enter_stake(self, stake: Decimal) -> None:
        rendered = f"{stake:.2f}"
        self.set_input_value(self.STAKE_INPUT, rendered)
        self.wait.until(
            lambda driver: driver.find_element(*self.STAKE_INPUT).get_attribute("value") == rendered
        )
        self.wait.until(EC.element_to_be_clickable(self.PLACE_BET))

    def read(self) -> SlipState:
        market = self.text(self.MARKET)
        prefix = self.MATCH_WINNER_PREFIX
        if not market.startswith(prefix):
            raise AssertionError(f"Slip market {market!r} does not name the selection")
        return SlipState(
            teams=" ".join(self.text(self.TEAMS).split()),
            selection=market[len(prefix) :].strip(),
            odds=parse_amount(self.text(self.ODDS).replace(self.ODDS_PREFIX, "")),
            stake=parse_amount(self.text(self.TOTAL_STAKE)),
            potential_payout=parse_amount(self.text(self.POTENTIAL_PAYOUT)),
        )

    def place(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.PLACE_BET)).click()

    def shows_placing(self) -> bool:
        # The button copy is "Placing...". The stylesheet uppercases it.
        expected = self.PLACING.casefold()
        try:
            WebDriverWait(self.driver, 3).until(
                lambda driver: expected in driver.find_element(*self.PLACE_BET).text.casefold()
            )
            return True
        except TimeoutException:
            return False

    def has_no_active_selection(self) -> bool:
        if self.present(self.TEAMS):
            return False
        return self.text(self.EMPTY) == self.EMPTY_SLIP and self.text(self.COUNT) == "0"
