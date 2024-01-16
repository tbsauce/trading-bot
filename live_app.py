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

data = bot.get_bars_data(symbol, time_frame, start_date, end_date, feed)

# Donchian Channel
data_donchian_channels = bot.get_donchian_channel(96, symbol, time_frame, start_date, end_date, feed)

# Volume Bars
data_volume = bot.get_volume(data)

# Volume MA
data_vma = bot.get_volume_moving_average(30, symbol, time_frame, start_date, end_date, feed)

# Williams %R 
data_williams_r = bot.get_williams_r(200, symbol, time_frame, start_date, end_date, feed)

exit(1)
plt.figure(figsize=(10, 6))

# Plot Donchian Channel
plt.plot(data['t'], data['c'], linestyle='-')
plt.plot(data['t'], data_donchian_channels['upper_band'], label='Upper Band', linestyle='--', color='blue')
plt.plot(data['t'], data_donchian_channels['middle_band'], label='Middle Band', linestyle='--', color='blue')
plt.legend()
plt.show()