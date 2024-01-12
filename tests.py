from bot import Bot
import matplotlib.pyplot as plt

bot = Bot()

symbol = "TSLA"
time_frame = "1Min"
start_date = "2022-04-11T09:00:00Z"
end_date = "2022-04-11T11:30:00Z"
feed = "sip"

data = bot.get_historical_data(symbol, time_frame, start_date, end_date, feed)

# Donchian Channel
# data_donchian_channels = bot.get_donchian_channel(20, symbol, time_frame, start_date, end_date, feed)

# plt.figure(figsize=(10, 6))
# plt.plot(data['t'], data['c'], marker='o', linestyle='-')
# plt.plot(data['t'], data_donchian_channels['upper_band'], label='Upper Band', linestyle='--', color='red')
# plt.plot(data['t'], data_donchian_channels['middle_band'], label='Middle Band', linestyle='--', color='red')
# plt.plot(data['t'], data_donchian_channels['lower_band'], label='Lower Band', linestyle='--', color='red')
# plt.xlabel('Time')
# plt.ylabel('Closing Price')
# plt.xticks(rotation=90)
# plt.tight_layout()
# plt.show()


#Volume Bars
# data_volume = bot.get_volume(data)

# temp_positive = data_volume['volume_adjusted'].abs()
# plt.bar(data_volume['t'], temp_positive, color=['g' if x >= 0 else 'r' for x in data_volume['volume_adjusted']])
# plt.xlabel('Time')
# plt.ylabel('Volume')
# plt.xticks(rotation=90)
# plt.tight_layout()
# plt.show()


# Williams %R
# data_williams_r = bot.get_williams_r(14, symbol, time_frame, start_date, end_date, feed)

# plt.figure(figsize=(10, 6))
# plt.plot(data_williams_r['t'], data_williams_r['WilliamsR'], linestyle='-')

# plt.axhline(y=-20, color='r', linestyle='--', label='Horizontal Line at y=5')
# plt.axhline(y=-80, color='r', linestyle='--', label='Horizontal Line at y=5')

# plt.xlabel('Time')
# plt.ylabel('Closing Price')
# plt.xticks(rotation=90)
# plt.tight_layout()
# plt.show()
