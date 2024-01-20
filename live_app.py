from bot import Bot
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime, timedelta

bot = Bot()

symbol = "TSLA"
time_frame = "5Min"
feed = "iex"

#Get Current Date
start_date = datetime.now().date()
end_date = start_date + timedelta(days=1)
#convert to desired format
start_date = start_date.strftime('%Y-%m-%dT00:00:00Z')
end_date = end_date.strftime('%Y-%m-%dT00:00:00Z')

trade = 0
buy = 1
while True:

    # Bars data
    data = bot.get_bars_data(symbol, time_frame, start_date, end_date, feed)
    # Donchian Channel
    data_donchian_channels = bot.get_donchian_channel(96, symbol, time_frame, start_date, end_date, feed)

    # Volume Bars
    data_volume = bot.get_volume(data)

    # Volume MA
    data_vma = bot.get_volume_moving_average(30, symbol, time_frame, start_date, end_date, feed)

    # Williams %R 
    data_williams_r = bot.get_williams_r(200, symbol, time_frame, start_date, end_date, feed)

    #Buying Strategy
    closing = data['c'].iloc[-1]
    print(f"Closing -> {closing} at Time -> {data['t'].iloc[-1]}")
    upper = data_donchian_channels['upper_band'].iloc[-1]
    middle = data_donchian_channels['middle_band'].iloc[-1]

    good_to_buy = (upper <= closing and 
        data_volume['volume_bars'].iloc[-1] > 0 and data_volume['volume_bars'].iloc[i -1] > 0 and
        data_vma['volume_ma'].iloc[-1] < data_volume['volume_bars'].iloc[-1] and
        data_vma['volume_ma'].iloc[i-1] < data_volume['volume_bars'].iloc[i-1] and
        data_volume['volume_bars'].iloc[-1] > data_volume['volume_bars'].iloc[i-1] and 
        data_williams_r['WilliamsR'].iloc[-1] >= -20)


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

    #update stop loss here
    if sell_down < middle:
        # bot.update_stock(id, middle)

    # Every 5min 
    time.sleep(30 * 2 * 5)
