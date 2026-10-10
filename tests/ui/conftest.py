import pytest
from selenium import webdriver

from api.client import BettingApi
from config.config import BROWSER, HEADLESS, PAGE_TIMEOUT_SECONDS
from pages.betting_page import BettingPage


@pytest.fixture
def api() -> BettingApi:
    return BettingApi()


@pytest.fixture
def balance_reset(api):
    """Reset before the browser opens, and keep both the response and the persisted balance."""
    reset_payload = api.reset_balance()
    persisted = api.get_balance()
    return {"reset": reset_payload, "persisted": persisted}


@pytest.fixture
def driver():
    if BROWSER != "chrome":
        pytest.fail(f"This framework drives Chrome. BROWSER={BROWSER!r} is not supported.")
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(PAGE_TIMEOUT_SECONDS)
    yield browser
    browser.quit()


@pytest.fixture
def app(driver, balance_reset):
    """Open the app after the balance reset fixture has run."""
    page = BettingPage(driver)
    page.open()
    return page
