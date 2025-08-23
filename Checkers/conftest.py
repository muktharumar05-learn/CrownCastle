import pytest
from playwright.sync_api import sync_playwright

URL = "https://www.gamesforthebrain.com/game/checkers/"

# ---------------- Fixtures ----------------

@pytest.fixture(scope="session")
def playwright_instance():
    """Start Playwright once per test session."""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Launch browser once per test session."""
    browser = playwright_instance.chromium.launch(headless=False)  # headless=True for CI/CD
    yield browser
    browser.close()

@pytest.fixture
def new_page(browser):
    """Create a new page per test function."""
    page = browser.new_page()
    yield page
    page.close()

@pytest.fixture
def page(new_page):
    """Navigate to the checkers game and return page object."""
    new_page.goto(URL, wait_until="load", timeout=6000)
    return new_page
