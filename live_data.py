import requests
import json
import time

# Function to get stock data and print it
def fetch_and_print_stock_data():
    url = "https://data.alpaca.markets/v2/stocks/bars/latest?symbols=TSLA&feed=iex"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": "PKIPW6JUBW9OS2K4IHB2",
        "APCA-API-SECRET-KEY": "GIW5OQCpieNsYQpeEvF4FmCbnSbhUtoUbCkrKulZ"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Request failed with status code:", response.status_code)
        return

    json_data = response.json()

    # Print the fetched data to the terminal
    print(json.dumps(json_data, indent=4))  # Print with indentation for readability

# Fetch and print data every minute continuously
while True:
    fetch_and_print_stock_data()
    time.sleep(60)  # Wait for 60 seconds (1 minute) before fetching again
