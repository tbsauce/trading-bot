import requests
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta

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
    
    def get_live_data(self):
        url = "https://data.alpaca.markets/v2/stocks/bars/latest?symbols=TSLA&feed=iex"


        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
            return

        data = response.json()
        
        return pd.DataFrame(data)

    def get_market_time(self, day):
        url = f"https://paper-api.alpaca.markets/v2/calendar?start={day}&end={day}"

        response = requests.get(url, headers=self.headers)

        #Catch Errors
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
            exit(1)

        data = response.json()[0]

        return data["open"], data["close"]


    def get_historical_data(self, symbol ,time_frame, start_date, end_date, feed):
        
        page_token = 0
        data = []
        while True:

            if page_token == 0:
                url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={time_frame}&start={start_date}&end={end_date}&adjustment=raw&feed={feed}&sort=asc"
            elif page_token == None:
                break
            else:
                url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={time_frame}&start={start_date}&end={end_date}&adjustment=raw&feed={feed}&page_token={page_token}&sort=asc"
        
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
        
    def get_donchian_channel(self, n_period, symbol ,time_frame, start_date, end_date, feed):
        
        #Save Start Date
        middle_date = start_date

        #Calculate New Start Date
        days_to_add = 2
        original_date = datetime.fromisoformat(start_date)
        start_date = original_date - timedelta(days=days_to_add)
        start_date = start_date.replace(tzinfo=None).isoformat() + "Z"

        #Get Historical Data
        df = self.get_historical_data(symbol, time_frame, start_date, end_date, feed)

        # Get num of extra lines
        # filtered_df = df[(df['t'] >= start_date) & (df['t'] <= middle_date)]
        # num_lines = len(filtered_df)

        #Calculate Donchian Lines
        df['upper_band'] = df['h'].rolling(window=n_period).max().shift(1)
        df['lower_band'] = df['l'].rolling(window=n_period).min().shift(1)
        df['middle_band'] = ((df['upper_band'] + df['lower_band']) / 2)

        return df[(df['t'] >= middle_date) & (df['t'] <= end_date)]

    def get_williams_r(self, df, n_period):
        
        df['highest_high'] = df['h'].rolling(window=n_period).max()
        df['lowest_low'] = df['l'].rolling(window=n_period).min()
        williams_r = ((df['highest_high']  - df['c']) / (df['highest_high']  - df['lowest_low'])) * -100

        df['WilliamsR'] = williams_r

        return df

    def get_volume(self, df):
        df['volume_adjusted'] = df['v']
        df.loc[df['c'] < df['c'].shift(1), 'volume_adjusted'] *= -1
        return df





