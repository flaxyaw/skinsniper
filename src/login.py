import time
from config import account
from driver import WebDriver

def login(driver: WebDriver, on_login_success):    
    driver.get("https://skinport.com/signin")
    time.sleep(5)

    current_url = driver.chrome.current_url

    if current_url.endswith("/account"):
        # We are logged in already
        print("Logged in.")
        on_login_success()
        #start_sniping()
    else:
        # We are not logged in yet
        print("Logging in...");
        email_input = driver.find_id("email")
        password_input = driver.find_id("password")
        
        # Fill in the login form
        email_input.send_keys(account["email"])
        password_input.send_keys(account["password"])
        password_input.submit()
        time.sleep(5)
        
        # Check if we need to confirm a new device
        current_url = driver.chrome.current_url
        if current_url.endswith("/confirm-new-device"):
            print(f"Please check the email {account['email']}. Paste the confirmation link here:")
            confirm_link = input()
            print(f"Confirming device...")
            driver.get(confirm_link) # Opens the confirmation link from the email to verify the device
            time.sleep(5)
            current_url = driver.chrome.current_url
            if current_url.endswith("/de/"): # We will be redirected to the homepage if the device was confirmed successfully
                on_login_success()
            else:
                print("Something went wrong. Please try again.")
                print(current_url)
        else:
            print("Something went wrong. Please try again.")
            print(current_url)