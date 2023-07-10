import json
from driver import WebDriver
from item import Item
from config import filter
from colorama import Fore

def read_live_data(driver: WebDriver):
    try:
        for wsData in driver.chrome.get_log('performance'): # Chrome logs all websocket messages as performance logs
            wsJson = json.loads((wsData['message'])) # Parse the message as JSON
            if wsJson["message"]["method"]== "Network.webSocketFrameReceived": # Check if the message is a websocket frame
                payload = wsJson["message"]["params"]["response"]["payloadData"]; # Get the payload of the websocket frame
                if payload.startswith("42"): # Check if the payload is a socket.io message (4 = message type, 2 = socket.io message)
                    message = json.loads(payload[2:]) # Parse the socket.io message as JSON, the first two characters are not part of the JSON because they are the message type from socket.io
                    if message[0] == "saleFeed":
                        sale_feed = message[1]
                        sales = sale_feed["sales"]
                        handle_new_sales(sales)
    except Exception as e:
        print(f"{Fore.RED}Error while reading live data. Retrying...")
        print(e)
                    
# This function is called when new sales are detected in the live feed
def handle_new_sales(sales):    
    for sale in sales:
        sale = Item(**sale)
        sale_price = sale.salePrice / 100
        suggested_price = sale.suggestedPrice / 100
        percentage = round(((sale_price / suggested_price) - 1) * 100, 2)
        sale_status = sale.saleStatus
        link = f"https://skinport.com/de/item/{sale.url}/{sale.saleId}"
        
        # Apply filter from config
        filtered = False
        if  sale_price < filter["min_price"] or \
            sale_price > filter["max_price"] or \
            percentage > filter["min_percentage"] or \
            sale_status == "sold":
                filtered = True
                if filter["debug_show_filtered"]:
                    print(f"(FILTERED) {Fore.RESET} • {Fore.GREEN}{sale.marketHashName} {Fore.RESET}for {Fore.BLUE}{sale_price} {sale.currency} {Fore.RESET}({Fore.RED}{percentage}%{Fore.RESET}) {link}")
        if filtered:
            continue
        
        print(f"{Fore.RESET} • {Fore.GREEN}{sale.marketHashName} {Fore.RESET}for {Fore.BLUE}{sale_price} {sale.currency} {Fore.RESET}({Fore.RED}{percentage}%{Fore.RESET}) {link}")
