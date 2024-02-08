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
    def get_account_balance(self):

        url = "https://paper-api.alpaca.markets/v2/account"

        response = requests.get(url, headers=self.headers)

        return response.json()['portfolio_value']

    def order_stock(self, symbol, qty, side, stop_price):
        url = "https://paper-api.alpaca.markets/v2/orders"

        order_params = {
            "symbol": symbol,
            "qty": qty,  # Number of shares to trade
            "side": side,
            "type": "market",  # Immediate market order
            "stop_price": stop_price,  # Stop price for the stop-loss order
            "time_in_force": "gtc",  # Good 'til Canceled
        }

        response = requests.post(url, json=order_params, headers=self.headers)

        # Check the response
        if response.status_code == 200:
            print("Order placed successfully.")
            print(response.json())
        elif response.status_code == 403:
            print("Forbidden: Buying power or shares are not sufficient.")
        elif response.status_code == 422:
            print("Unprocessable: Input parameters are not recognized.")
        else:
            print("Error:", response.status_code, response.text)
    
    def update_stock(self, id, stop_price):
        url = f"https://paper-api.alpaca.markets/v2/orders/{id}"

        order_params = {
            "stop_price": stop_price,  # Stop price for the stop-loss order
        }

        response = requests.post(url, json=order_params, headers=self.headers)

        # Check the response
        if response.status_code == 200:
            print("Order placed successfully.")
            print(response.json())
        elif response.status_code == 403:
            print("Forbidden: Buying power or shares are not sufficient.")
        elif response.status_code == 422:
            print("Unprocessable: Input parameters are not recognized.")
        else:
            print("Error:", response.status_code, response.text)

    
    def get_live_trade_data(self, symbol, feed):

        url = f"https://data.alpaca.markets/v2/stocks/bars/latest?symbols={symbol}&feed={feed}"

        response = requests.get(url, headers=self.headers)

        data = response.json()

        return pd.DataFrame(data)
        
    def get_trading_data(self, symbol ,start_date, end_date, feed):
        
        page_token = 0
        data = []
        while True:
            if page_token == 0:
                url = f"https://data.alpaca.markets/v2/stocks/trades?symbols={symbol}&start={start_date}&end={end_date}&feed={feed}&sort=asc"

            elif page_token == None:
                break
            else:
                url = f"https://data.alpaca.markets/v2/stocks/trades?symbols={symbol}&start={start_date}&end={end_date}&feed={feed}&page_token={page_token}&sort=asc"
        
            response = requests.get(url, headers=self.headers)

            #Catch Errors
            if response.status_code != 200:
                print("Request failed with status code:", response.status_code)
                exit(1)

            # Extracting data
            tmp_data = response.json()
            page_token = tmp_data['next_page_token']

            #Catch Formatation Errors
            if 'message' in tmp_data:
                print(tmp_data)
                exit(1)

            
            data.extend(tmp_data['trades'][symbol])

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


    def get_bars_data(self, symbol ,time_frame, start_date, end_date, feed):
        
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
                exit(1)

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
        days_to_add = 5
        original_date = datetime.fromisoformat(start_date)
        start_date = original_date - timedelta(days=days_to_add)
        start_date = start_date.replace(tzinfo=None).isoformat() + "Z"

        #Get Historical Data
        df = self.get_bars_data(symbol, time_frame, start_date, end_date, feed)

        # Get num of extra lines
        # filtered_df = df[(df['t'] >= start_date) & (df['t'] <= middle_date)]
        # num_lines = len(filtered_df)

        #Calculate Donchian Lines
        df['upper_band'] = df['h'].rolling(window=n_period).max().shift(1)
        df['lower_band'] = df['l'].rolling(window=n_period).min().shift(1)
        df['middle_band'] = ((df['upper_band'] + df['lower_band']) / 2)

        return df[(df['t'] >= middle_date) & (df['t'] <= end_date)]

    def get_williams_r(self, n_period, symbol ,time_frame, start_date, end_date, feed):
        
        #Save Start Date
        middle_date = start_date

        #Calculate New Start Date
        days_to_add = 5
        original_date = datetime.fromisoformat(start_date)
        start_date = original_date - timedelta(days=days_to_add)
        start_date = start_date.replace(tzinfo=None).isoformat() + "Z"

        #Get Historical Data
        df = self.get_bars_data(symbol, time_frame, start_date, end_date, feed)

        df['highest_high'] = df['h'].rolling(window=n_period).max()
        df['lowest_low'] = df['l'].rolling(window=n_period).min()
        williams_r = ((df['highest_high']  - df['c']) / (df['highest_high']  - df['lowest_low'])) * -100

        df['WilliamsR'] = williams_r

        return df[(df['t'] >= middle_date) & (df['t'] <= end_date)]

    def get_volume(self, df):

        df['volume_bars'] = df['v']
        df.loc[df['c'] < df['c'].shift(1), 'volume_bars'] *= -1
        
        return df
    
    def get_volume_moving_average(self, n_period, symbol ,time_frame, start_date, end_date, feed):

        #Save Start Date
        middle_date = start_date

        #Calculate New Start Date
        days_to_add = 5
        original_date = datetime.fromisoformat(start_date)
        start_date = original_date - timedelta(days=days_to_add)
        start_date = start_date.replace(tzinfo=None).isoformat() + "Z"

        #Get Historical Data
        df = self.get_bars_data(symbol, time_frame, start_date, end_date, feed)

        df['volume_ma'] = df['v'].rolling(window=n_period).mean()

        return df[(df['t'] >= middle_date) & (df['t'] <= end_date)]

    def calculate_trade_stats(self, signals):
        total_profit_loss = 0
        winning_trades = 0
        value_w = 0
        losing_trades = 0
        value_l = 0
        buy_price = 0
        num_trades = 0

        # Remove all holds
        signals = [value for value in signals if value != 0]

        #get even size
        size = len(signals)
        if size % 2 != 0:
            size = size - 1
            
        for i in range(0, size, 2):
            profit = (signals[i + 1] * -1) - signals[i]
            total_profit_loss += profit
            if profit < 0:
                losing_trades += 1
                value_l += profit
            else:
                winning_trades += 1
                value_w += profit
            num_trades += 1
        winning_percentage = (winning_trades / num_trades) * 100 if num_trades > 0 else 0

        return {
            'total_profit_loss': total_profit_loss,
            'num_trades': num_trades,
            'winning_trades': winning_trades,
            'value_of_winning_trades': value_w,
            'losing_trades': losing_trades,
            'value_of_loosing_trades': value_l,
            'winning_percentage': round(winning_percentage, 2) if num_trades > 0 else 0
        }




