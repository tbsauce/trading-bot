import requests
from dotenv import load_dotenv
import os

import pandas as pd

class Bot:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        #Inictialize Alpaca Headers
        self.headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": os.environ.get("KEY_ID"),
            "APCA-API-SECRET-KEY": os.environ.get("SECRET_KEY")
        }

    def get_market_time(self, day):
        url = f"https://paper-api.alpaca.markets/v2/calendar?start={day}&end={day}"

        response = requests.get(url, headers=self.headers)

        #Catch Errors
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
            exit(1)

        data = response.json()[0]

        return data["open"], data["close"]


    def get_historical_data(self, symbol ,time_frame, start, end, feed):

        page_token = 0
        data = []
        while True:

            if page_token == 0:
                url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={time_frame}&start={start}&end={end}&adjustment=raw&feed={feed}&sort=asc"
            elif page_token == None:
                break
            else:
                url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={time_frame}&start={start}&end={end}&adjustment=raw&feed={feed}&page_token={page_token}&sort=asc"
        
            response = requests.get(url, headers=self.headers)

            #Catch Errors
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
            
            # Extracting data
            tmp_data = response.json()
            page_token = tmp_data['next_page_token']

            #Catch Formatation Errors
            if 'message' in tmp_data:
                print(tmp_data)
                exit(1)

            
            data.extend(tmp_data['bars'][symbol])

        return pd.DataFrame(data)
        
    def get_donchian_channel(self, df):
        n_period = 10 
        df['upper_band'] = df['c'].rolling(window=n_period).max().shift(1)
        df['lower_band'] = df['c'].rolling(window=n_period).min().shift(1)
        df['middle_band'] = ((df['upper_band'] + df['lower_band']) / 2)

        return df
