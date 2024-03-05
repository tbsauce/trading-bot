from bot import Bot
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime, timedelta
import pandas as pd

import json

bot = Bot()

symbol = "TSLA"
time_frame = "1Min"
feed = "iex"

#Get Current Date
end_date = datetime.now().date()
start_date = end_date + timedelta(days=-1)
#convert to desired format
start_date = start_date.strftime('%Y-%m-%dT00:00:00Z')
end_date = end_date.strftime('%Y-%m-%dT00:00:00Z')

trade = 0
buy = 1

data = pd.DataFrame() 
while True:

    # Bars data
    new_data = bot.get_live_trade_data(symbol, feed)

    data = pd.concat([data, new_data], ignore_index=True)

    #Save Start Date
    middle_date = start_date

    #Calculate New Start Date
    days_to_add = 5
    
    original_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
    start_date = original_date - timedelta(days=days_to_add)
    start_date = start_date.replace(tzinfo=None).isoformat() + "Z"

    #Get Historical Data
    df = bot.get_bars_data(symbol, time_frame, start_date, end_date, feed)

    df = pd.concat([df, data], ignore_index=True)

    #Donchian Channel
    df['upper_band'] = df['h'].rolling(window=480).max().shift(1)
    df['lower_band'] = df['l'].rolling(window=480).min().shift(1)
    df['middle_band'] = ((df['upper_band'] + df['lower_band']) / 2)

    data_donchian_channels = df[(df['t'] >= middle_date) & (df['t'] <= end_date)]

    # Volume Bars

    df['volume_bars'] = df['v']
    df.loc[df['c'] < df['c'].shift(1), 'volume_bars'] *= -1
    data_volume = df

    # Volume MA
    
    df['volume_ma'] = df['v'].rolling(window=50).mean()

    data_vma =  df[(df['t'] >= middle_date) & (df['t'] <= end_date)]

    # Williams %R 
    df['highest_high'] = df['h'].rolling(window=200).max()
    df['lowest_low'] = df['l'].rolling(window=200).min()
    williams_r = ((df['highest_high']  - df['c']) / (df['highest_high']  - df['lowest_low'])) * -100

    df['WilliamsR'] = williams_r

    data_williams_r = df[(df['t'] >= middle_date) & (df['t'] <= end_date)]

    #Buying Strategy
    closing = data.iloc[-1]["bars"]["c"]
    date = data.iloc[-1]["bars"]["t"]
    print(f"Closing -> {closing} at Time -> {date}")
    upper = data_donchian_channels['upper_band'].iloc[-1]
    middle = data_donchian_channels['middle_band'].iloc[-1]
    sell_down = sell_up = data_donchian_channels['middle_band'].iloc[-1]

    good_to_buy = (upper <= closing and 
        data_volume['volume_bars'].iloc[-1] > 0 and data_volume['volume_bars'].iloc[-2] > 0 and
        data_vma['volume_ma'].iloc[-1] < data_volume['volume_bars'].iloc[-1] and
        data_vma['volume_ma'].iloc[i-1] < data_volume['volume_bars'].iloc[-2] and
        data_volume['volume_bars'].iloc[-1] > data_volume['volume_bars'].iloc[-2] and 
        data_williams_r['WilliamsR'].iloc[-1] >= -20)


    #update stop loss here
    if sell_down < middle:
        # bot.update_stock(id, middle)
        sell_down = middle
    
    print(f"sellDown -> {sell_down}, middle -> {middle}, closing -> {closing}")

    #here buy what but first chck if theres any bought stocks
    if buy and good_to_buy:
        sell_down = middle
        #get qty of stocks for all the balance money
        qty = math.floor(bot.get_account_balance() / closing)
        print(f"qty -> {qty}")
        #bot.order_stock(symbol, qty, "buy", middle)
        # the one vefore shoudl return id
        buy = 0
    elif not buy and closing <= sell_down:
        buy = 1
        print(f"Sold -> {closing}")
        
    
    

    time.sleep(60)
