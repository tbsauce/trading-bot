from bot import Bot
import matplotlib.pyplot as plt

bot = Bot()

# Call the get_market_time method
open_time , close_time = bot.get_market_time("2022-01-03")

print(open_time)
print(close_time)

data = bot.get_historical_data("TSLA", "1Min", "2022-01-03T00:00:00Z", "2022-01-03T11:30:00Z", "sip")
print(data['c'])

data = bot.get_donchian_channel(data)

# Plotting the closing values over time
plt.figure(figsize=(10, 6))
plt.plot(data['t'], data['c'], marker='o', linestyle='-')
plt.plot(data['upper_band'], label='Upper Band', linestyle='--', color='red')
plt.plot(data['middle_band'], label='Middle Band', linestyle='--', color='red')
plt.plot(data['lower_band'], label='Lower Band', linestyle='--', color='red')
plt.title('TSLA Closing Prices')
plt.xlabel('Time')
plt.ylabel('Closing Price ($)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

