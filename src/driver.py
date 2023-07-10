import pathlib

from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebDriver:
    def __init__(self, headless=False):
        # The chrome_data folder is used to store the cookies and session data of the Chrome browser
        # This makes it possible to login to Skinport once and then use the same session for all future runs of the script
        chrome_data_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/chrome_data"
        
        # The driver is used to control the Chrome browser
        self.chrome = Driver(uc=True, chromium_arg=f"--user-data-dir={chrome_data_path}", uc_cdp_events=True, headless=headless)
        self.wait = WebDriverWait(self.chrome, 10)
        
    # Find any HTML element by its id, wait until it is present and return it
    def find_id(self, id):
        self.wait.until(EC.presence_of_element_located((By.ID, id)))
        return self.chrome.find_element(By.ID, id)

    # Find any HTML element by its class, wait until it is present and return it
    def find_class(self, class_name):
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        return self.chrome.find_element(By.CLASS_NAME, class_name)
    
    def get(self, url):
        self.chrome.get(url)
    
    def quit(self):
        self.chrome.quit()