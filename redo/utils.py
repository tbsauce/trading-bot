import requests
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

from itertools import product

# Load environment variables
load_dotenv()

# Initialize Alpaca Headers
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": os.environ.get("KEY_ID"),
    "APCA-API-SECRET-KEY": os.environ.get("SECRET_KEY")
}

def get_bars_data(data_frame, symbol ,time_frame, start_date, feed):
    try:
    
        next_token = None
        
        # While to get all pages with data
        while True:
            # URL for the API request
            url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={time_frame}&start={start_date}&limit=1000&adjustment=raw&feed={feed}&sort=asc"
            if next_token:
                url += f"&page_token={next_token}"
                
            # make request to API
            response = requests.get(url, headers=headers).json()
            df = pd.DataFrame(response["bars"]["TSLA"])
            data_frame = pd.concat([data_frame, df], ignore_index=True)
        

            # If there is no next_token leave loop
            next_token = response['next_page_token']
            if not next_token:
                break

    except:
        print("unexpected error getting bars from API")

    
    return data_frame.drop_duplicates()

def get_donchian_channel(data_frame, n_period, offset):

    data_frame['lower'] = data_frame['l'].rolling(window=n_period).min().shift(offset)
    data_frame['upper'] = data_frame['h'].rolling(window=n_period).max().shift(offset)
    data_frame['middle'] = ((data_frame['upper'] + data_frame['lower']) / 2).shift(offset)

    return data_frame

def get_volume(data_frame):

    data_frame['volume_bars'] = data_frame['v']
    data_frame.loc[data_frame['c'] < data_frame['c'].shift(1), 'volume_bars'] *= -1
    
    return data_frame

def get_volume_moving_average(data_frame, n_period):

    data_frame['volume_ma'] = data_frame['v'].rolling(window=n_period).mean()

    return data_frame

def get_williams_r(data_frame, n_period):

    highest = data_frame['h'].rolling(window=n_period).max()
    lowest = data_frame['l'].rolling(window=n_period).min()

    data_frame['WilliamsR'] = ((highest - data_frame['c']) / (highest - lowest)) * -100
    
    return data_frame

def strategy(data_frame, stop_loss_percent, stop_gain_percent):

    # Initialize variables
    trade_active = False
    entry_price = None
    stop_loss_price = None

    # Initialize all rows as 'HOLD'/0
    data_frame['Trade Action'] = 0.0

    for index, row in data_frame.iterrows():
        # Entry Condition
        if( not trade_active and row['c'] >= row['upper'] and row['WilliamsR'] >= -20 and row['v'] > row['volume_ma'] and row['volume_bars'] > 0):
            
            trade_active = True
            entry_price = row['c']
            stop_loss_price = entry_price * (1 - stop_loss_percent / 100)
            stop_gain_price = entry_price * (1 + stop_gain_percent / 100)
            # Initialize row as 'BUY'/1
            data_frame.at[index, 'Trade Action'] = entry_price

        # Exit Condition and Initialize rows as 'SELL'/-1
        elif trade_active:
            if row['c'] <= stop_loss_price:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * stop_loss_price

            elif row['c'] >= stop_gain_price:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * stop_gain_price
    
            elif row['c'] < row['middle']:
                trade_active = False
                data_frame.at[index, 'Trade Action'] = -1 * row['middle']


    return data_frame

def calculate_trade_stats(data_frame):

    total_profit_loss = 0
    profit_loss_values = []
    winning_trades = 0
    value_w = 0
    losing_trades = 0
    value_l = 0
    num_trades = 0

    buy_price = None

    # Iterate through the data_frame and identify BUY/SELL trades
    for index, row in data_frame.iterrows():
        trade_action = row['Trade Action']
        
        # buy action
        if trade_action > 0:
            buy_price = trade_action
        
        # sell action
        elif trade_action < 0:
            sell_price = trade_action * -1
            profit_or_loss = sell_price - buy_price
            

            # Update overall stats
            total_profit_loss += profit_or_loss
            profit_loss_values.append(total_profit_loss)
            if profit_or_loss < 0:  # It's a losing trade
                losing_trades += 1
                value_l += profit_or_loss
            else:  # It's a winning trade
                winning_trades += 1
                value_w += profit_or_loss
            num_trades += 1
            
            # Reset buy price
            buy_price = None

    winning_percentage = (winning_trades / num_trades) * 100 if num_trades > 0 else 0
    loosing_percentage = (losing_trades / num_trades) * 100 if num_trades > 0 else 0
    

    # # Plot the profit/loss over time from the 'profit_loss_values' list
    # plt.plot(profit_loss_values, label="Profit/Loss Over Time", color='green')
    # plt.title('Profit and Loss Over Time')
    # plt.xlabel('Trade Number')
    # plt.ylabel('Profit/Loss')
    # plt.grid(True)
    # plt.legend()
    #
    # # Save the graph as an image file
    # graph_filename = 'profit_loss_graph.png'
    # plt.savefig(graph_filename)

    # Return the final trade statistics
    stats = {
        'total_profit_loss': total_profit_loss,
        'num_trades': num_trades,
        'winning_trades': winning_trades,
        'value_of_winning_trades': value_w,
        'losing_trades': losing_trades,
        'value_of_loosing_trades': value_l,
        'winning_percentage': round(winning_percentage, 2) if num_trades > 0 else 0,
        'loosing_percentage': round(loosing_percentage, 2) if num_trades > 0 else 0
    }
    
    return stats
