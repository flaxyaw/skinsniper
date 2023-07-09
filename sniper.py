import json
import time
import pathlib
import signal
from config import *    
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init as colorama_init
from colorama import Fore

colorama_init()
print(Fore.CYAN);
print("                                                                       ")
print("██╗  ██╗ █████╗ ████████╗ ██████╗ ███████╗███╗   ██╗██╗██████╗ ███████╗")
print("██║ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝████╗  ██║██║██╔══██╗██╔════╝")
print("█████╔╝ ███████║   ██║   ██║   ██║███████╗██╔██╗ ██║██║██████╔╝█████╗  ")
print("██╔═██╗ ██╔══██║   ██║   ██║   ██║╚════██║██║╚██╗██║██║██╔═══╝ ██╔══╝  ")
print("██║  ██╗██║  ██║   ██║   ╚██████╔╝███████║██║ ╚████║██║██║     ███████╗")
print("╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚══════╝")
print("                                                                       ")
print("Loading... 01001011 01100001 01110100 01101111 01010011 01101110 01101001 01110000 01100101 ")
print("BB Enjoy.")
print(Fore.BLUE);

# The chrome_data folder is used to store the cookies and session data of the Chrome browser
# This makes it possible to login to Skinport once and then use the same session for all future runs of the script
chrome_data_path = f"{pathlib.Path(__file__).parent.absolute()}/chrome_data"

# The driver is used to control the Chrome browser
driver = Driver(uc=True, chromium_arg=f"--user-data-dir={chrome_data_path}", uc_cdp_events=True, headless=False)
wait = WebDriverWait(driver, 10)

# Handle CTRL+C
def exit_handler(signum, frame):
    if input(f"{Fore.RED}Do you really want to stop? (y/n) ") == 'y':
        driver.quit()
        print("Byee!")
        exit(1)
 
signal.signal(signal.SIGINT, exit_handler)

# Find any HTML element by its id, wait until it is present and return it
def find_id(id):
    wait.until(EC.presence_of_element_located((By.ID, id)))
    return driver.find_element(By.ID, id)

# Find any HTML element by its class, wait until it is present and return it
def find_class(class_name):
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    return driver.find_element(By.CLASS_NAME, class_name)

def read_live_data():
    try:
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
    except:
        print("Error while reading live data. Retrying...")

                    
# This function is called when new sales are detected in the live feed
def handle_new_sales(sales):
    for sale in sales:
        # print(json.dumps(sale, indent=2)) # Prints whole sale object
        sale_price = sale["salePrice"] / 100
        suggested_price = sale["suggestedPrice"] / 100
        percentage = round(((sale_price / suggested_price) - 1) * 100, 2)
        sale_status = sale["saleStatus"]
        link = f"https://skinport.com/de/item/{sale['url']}/{sale['saleId']}"
        
        # Apply filter from config
        filtered = False
        if  sale_price < filter["min_price"] or \
            sale_price > filter["max_price"] or \
            percentage > filter["min_percentage"] or \
            sale_status == "sold":
                filtered = True
                if filter["debug_show_filtered"]:
                    print(f"(FILTERED) {Fore.RESET} • {Fore.GREEN}{sale['marketHashName']} {Fore.RESET}for {Fore.BLUE}{sale_price} {sale['currency']} {Fore.RESET}({Fore.RED}{percentage}%{Fore.RESET}) {link}")
        if filtered:
            continue
        
        print(f"{Fore.RESET} • {Fore.GREEN}{sale['marketHashName']} {Fore.RESET}for {Fore.BLUE}{sale_price} {sale['currency']} {Fore.RESET}({Fore.RED}{percentage}%{Fore.RESET}) {link}")

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
