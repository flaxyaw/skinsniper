import json
import time
import pathlib
from config import *    
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("   _____ _    _                 _                 ")
print("  / ____| |  (_)               (_)                ")
print(" | (___ | | ___ _ __  ___ _ __  _ _ __   ___ _ __ ")
print("  \___ \| |/ / | '_ \/ __| '_ \| | '_ \ / _ \ '__|")
print("  ____) |   <| | | | \__ \ | | | | |_) |  __/ |   ")
print(" |_____/|_|\_\_|_| |_|___/_| |_|_| .__/ \___|_|   ")
print("                                 | |              ")
print("                                 |_|              ")

# The chrome_data folder is used to store the cookies and session data of the Chrome browser
# This makes it possible to login to Skinport once and then use the same session for all future runs of the script
chrome_data_path = f"{pathlib.Path(__file__).parent.absolute()}/chrome_data"

# The driver is used to control the Chrome browser
driver = Driver(uc=True, chromium_arg=f"--user-data-dir={chrome_data_path}", uc_cdp_events=True, headless=False)
wait = WebDriverWait(driver, 10)

# Find any HTML element by its id, wait until it is present and return it
def find_id(id):
    wait.until(EC.presence_of_element_located((By.ID, id)))
    return driver.find_element(By.ID, id)

# Find any HTML element by its class, wait until it is present and return it
def find_class(class_name):
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    return driver.find_element(By.CLASS_NAME, class_name)

def read_live_data():
    for wsData in driver.get_log('performance'): # Chrome logs all websocket messages as performance logs
        wsJson = json.loads((wsData['message'])) # Parse the message as JSON
        if wsJson["message"]["method"]== "Network.webSocketFrameReceived": # Check if the message is a websocket frame
            payload = wsJson["message"]["params"]["response"]["payloadData"]; # Get the payload of the websocket frame
            if payload.startswith("42"): # Check if the payload is a socket.io message (4 = message type, 2 = socket.io message)
                message = json.loads(payload[2:]) # Parse the socket.io message as JSON, the first two characters are not part of the JSON because they are the message type from socket.io
                if message[0] == "saleFeed":
                    sale_feed = message[1]
                    sales = sale_feed["sales"]
                    handle_new_sales(sales)
                    
# This function is called when new sales are detected in the live feed
def handle_new_sales(sales):
    for sale in sales:
        print(f"+ {sale['marketHashName']} for {sale['salePrice'] / 100} {sale['currency']}")

# Starts the sniping process. It is called after the login process is completed
def start_sniping():
    # Open the market page of new items and click the "Live" button to start the live feed
    print("Start sniping...")
    driver.get("https://skinport.com/de/market?sort=date&order=desc")
    time.sleep(5)
    #time.sleep(500)
    live_button = find_class("LiveBtn")
    live_button.click()

    print("Listening for new sales...");        
    while True:
        read_live_data()
        time.sleep(0.05)

def login():    
    driver.get("https://skinport.com/signin")
    time.sleep(5)
    
    if driver.current_url.endswith("/account"):
        # We are logged in already
        print("Logged in.")
        start_sniping()
    else:
        # We are not logged in yet
        print("Logging in...");
        email_input = find_id("email")
        password_input = find_id("password")
        
        # Fill in the login form
        email_input.send_keys(account["email"])
        password_input.send_keys(account["password"])
        password_input.submit()
        time.sleep(5)
        
        # Check if we need to confirm a new device
        if driver.current_url.endswith("/confirm-new-device"):
            print(f"Please check the email {account['email']}. Paste the confirmation link here:")
            confirm_link = input()
            print(f"Confirming device...")
            driver.get(confirm_link) # Opens the confirmation link from the email to verify the device
            time.sleep(5)
            
            if driver.current_url.endswith("/de/"): # We will be redirected to the homepage if the device was confirmed successfully
                start_sniping()
            else:
                print("Something went wrong. Please try again.")
                print(driver.current_url)
        else:
            print("Something went wrong. Please try again.")
            print(driver.current_url)
                    
login()

print("Bye!");
driver.quit()
