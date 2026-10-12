from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from model import MatchSelection
from pages.base_page import BasePage
from utils.money import parse_amount


class MatchList(BasePage):
    MATCH_LIST = (By.XPATH, "//*[@id='match-list']")
    MATCH_CARD = (By.XPATH, "//*[starts-with(@id,'match-card-')]")
    TEAM_NAME = (By.XPATH, ".//*[contains(@class,'teamName')]")
    ODDS_VALUE = (By.XPATH, ".//*[contains(@class,'oddsButtonValue')]")

    def wait_until_loaded(self) -> None:
        self.wait.until(EC.visibility_of_element_located(self.MATCH_LIST))
        self.wait.until(lambda driver: driver.find_elements(*self.MATCH_CARD))

    def select_home_on_first_match(self) -> MatchSelection:
        """Select the Home (1) price on the first upcoming match in the list."""
        self.wait_until_loaded()
        card = self.driver.find_elements(*self.MATCH_CARD)[0]
        selection = self._read_home_selection(card)
        button = card.find_element(*self._home_odds(selection.match_id))
        button.click()
        self.wait.until(
            lambda driver: "oddsButtonSelected"
            in driver.find_element(*self._home_odds(selection.match_id)).get_attribute("class")
        )
        return selection

    @staticmethod
    def _home_odds(match_id: str) -> tuple[str, str]:
        return (By.XPATH, f"//*[@id='odds-{match_id}-home']")

    def _read_home_selection(self, card: WebElement) -> MatchSelection:
        card_id = card.get_attribute("id") or ""
        prefix = "match-card-"
        if not card_id.startswith(prefix) or card_id == prefix:
            raise AssertionError(f"Match card id {card_id!r} does not include a match id")
        match_id = card_id[len(prefix) :]
        team_names = [element.text.strip() for element in card.find_elements(*self.TEAM_NAME)]
        if len(team_names) < 2:
            raise AssertionError(f"Match card {match_id} did not show home and away teams")
        odds_button = card.find_element(*self._home_odds(match_id))
        odds_text = odds_button.find_element(*self.ODDS_VALUE).text
        return MatchSelection(
            match_id=match_id,
            home_team=team_names[0],
            away_team=team_names[1],
            odds=parse_amount(odds_text),
        )
