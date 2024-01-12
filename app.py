from bot import Bot
import matplotlib.pyplot as plt

bot = Bot()

data = bot.get_historical_data("TSLA", "1Min", "2022-01-03T00:00:00Z", "2022-01-03T11:30:00Z", "sip")

df = bot.get_volume(data)

# Plotting the closing values over time
temp_positive = df['volume_adjusted'].abs()
plt.bar(data['t'], temp_positive, color=['g' if x >= 0 else 'r' for x in df['volume_adjusted']])
plt.title('TSLA Closing Prices')
plt.xlabel('Time')
plt.ylabel('Closing Price ($)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
