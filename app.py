from bot import Bot
import matplotlib.pyplot as plt

bot = Bot()

symbol = "TSLA"
time_frame = "1Min"
start_date = "2022-04-11T09:00:00Z"
end_date = "2022-04-11T11:30:00Z"
feed = "sip"

data = bot.get_historical_data(symbol, time_frame, start_date, end_date, feed)

data_channel = bot.get_donchian_channel(20, symbol, time_frame, start_date, end_date, feed)

plt.figure(figsize=(10, 6))
plt.plot(data['t'], data['c'], marker='o', linestyle='-')

plt.plot(data['t'], data_channel['upper_band'], label='Upper Band', linestyle='--', color='red')
plt.plot(data['t'], data_channel['middle_band'], label='Middle Band', linestyle='--', color='red')
plt.plot(data['t'], data_channel['lower_band'], label='Lower Band', linestyle='--', color='red')

plt.xlabel('Time')
plt.ylabel('Closing Price')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

