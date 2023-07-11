import time
import signal
from driver import WebDriver
from login import login
from colorama import init as colorama_init
from colorama import Fore
from sales_handler import read_live_data
from notify import notify_send



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

notify_send("KatoSniper has been launched. Enjoy sniping ;)")
driver = WebDriver(headless=False)

# Handle CTRL+C
def exit_handler(signum, frame):
    if input(f"{Fore.RED}Do you really want to stop? (y/n) ") == 'y':
        driver.quit()
        notify_send("KatoSnipe has been closed.")
        print("Byee!")
        exit(1)
 
signal.signal(signal.SIGINT, exit_handler)

# Starts the sniping process. It is called after the login process is completed
def start_sniping():
    # Open the market page of new items and click the "Live" button to start the live feed
    print("Start sniping...")
    notify_send('Sniping started.') 
    driver.get("https://skinport.com/de/market?sort=date&order=desc")
    time.sleep(5)
    #time.sleep(500)
    live_button = driver.find_class("LiveBtn")
    live_button.click()

    print("Listening for new sales...");       
    notify_send('Listening for new Snipes.') 
    while True:
        read_live_data(driver)
        time.sleep(0.05)
    
login(driver, start_sniping)

print("Bye!")
driver.quit()
