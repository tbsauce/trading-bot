from bot import Bot

bot = Bot()

# Call the get_market_time method
open_time , close_time = bot.get_market_time("2022-01-03")

print(open_time)
print(close_time)

data = bot.get_historical_data("TSLA", "1", "2022-01-03T00:00:00Z", "2022-01-07T00:00:00Z", "sip")
print(data)