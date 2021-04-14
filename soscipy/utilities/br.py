import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

os.environ['WDM_LOG_LEVEL'] = '0'


class browser:
    def __init__(self, URL, headless=True, no_image=True) -> object:
        self.url = URL
        self.headless = headless
        self.no_image = no_image

    def setup(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        if self.no_image:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        elif not options:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        print('starting the browser')

    def close(self):
        self.driver.quit()
