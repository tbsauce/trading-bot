from utils import * 

def main():

    symbol = "TSLA"
    timeframe = "1H"
    feed="iex"
    start_date = (datetime.now() - timedelta(days=300)).date()

    data_frame = pd.DataFrame()
    data_frame = get_bars_data(data_frame, symbol, timeframe, start_date, feed)
    data_frame = get_donchian_channel(data_frame, 5, 4)
    data_frame = get_volume(data_frame)
    data_frame = get_volume_moving_average(data_frame, 45)
    data_frame = get_williams_r(data_frame, 20)
    data_frame = strategy(data_frame, 20, 40)
    stats = calculate_trade_stats(data_frame)

    
    print("Total Profit/Loss:", stats['total_profit_loss'])
    print("Number of Trades:", stats['num_trades'])
    print("Winning Trades:", stats['winning_trades'])
    print("Value of Winning Trades:", stats['value_of_winning_trades'])
    print("Losing Trades:", stats['losing_trades'])
    print("Value of Losing Trades:", stats['value_of_loosing_trades'])
    print("Winning Percentage:", stats['winning_percentage'], "%")
    print("Loosing Percentage:", stats['loosing_percentage'], "%")

# Funcion to get the best parameters for the strategy
def main_optimization():

    symbol = "TSLA"
    timeframe = "1H"
    feed = "iex"
    start_date = (datetime.now() - timedelta(days=300)).date()

    # Define parameter ranges
    donchian_period_range = range(5, 31, 5)  # Period from 5 to 30 with step 5
    donchian_offset_range = range(0, 10, 1)  # Offset from 0 to 9
    volume_ma_period_range = range(5, 101, 20)  # Volume MA period from 5 to 100 with step 20
    williams_period_range = range(5, 29, 5)  # Williams %R period from 5 to 28 with step 5
    total_iterations = len(donchian_period_range) * len(donchian_offset_range) * len(volume_ma_period_range) * len(williams_period_range)
    print("Total Interations: {total_iterations}")

    best_stats = None
    best_parameters = None

    # Load data only once, this will be used for all parameter combinations
    stock_data = get_bars_data(pd.DataFrame(), symbol, timeframe, start_date, feed)
    stock_data = get_volume(stock_data)

    # Now loop through the combinations of parameters
    for donchian_period, volume_ma_period, williams_period, donchian_offset in product(
        donchian_period_range, volume_ma_period_range, williams_period_range, donchian_offset_range
    ):
        try:
            # Copy the pre-loaded stock data for each iteration
            data_frame = stock_data.copy()

            # Apply the specific indicators for the current parameters
            data_frame = get_donchian_channel(data_frame, donchian_period, donchian_offset)
            data_frame = get_volume_moving_average(data_frame, volume_ma_period)
            data_frame = get_williams_r(data_frame, williams_period)

            # Apply the strategy and calculate trade stats
            data_frame = strategy(data_frame, 20, 40)
            stats = calculate_trade_stats(data_frame)

            # Update the best performing parameters
            if best_stats is None or stats['total_profit_loss'] > best_stats['total_profit_loss']:
                best_stats = stats
                best_parameters = (donchian_period, volume_ma_period, williams_period, donchian_offset)

        except Exception as e:
            print(f"Error during optimization with {donchian_period=}, {volume_ma_period=}, {williams_period=}, {donchian_offset=}: {e}")
            continue

    # Output the best parameters and performance stats after the loop
    print("\nBest Parameters:")
    print(f"  Donchian Period: {best_parameters[0]}")
    print(f"  Donchian Offset: {best_parameters[3]}")
    print(f"  Volume MA Period: {best_parameters[1]}")
    print(f"  Williams %R Period: {best_parameters[2]}")

    print("\nTrade Stats for Best Parameters:")
    print(f"  Total Profit/Loss: {best_stats['total_profit_loss']}")
    print(f"  Number of Trades: {best_stats['num_trades']}")
    print(f"  Winning Trades: {best_stats['winning_trades']}")
    print(f"  Value of Winning Trades: {best_stats['value_of_winning_trades']}")
    print(f"  Losing Trades: {best_stats['losing_trades']}")
    print(f"  Value of Losing Trades: {best_stats['value_of_loosing_trades']}")
    print(f"  Winning Percentage: {best_stats['winning_percentage']}%")
    print(f"  Losing Percentage: {best_stats['losing_percentage']}%")

if __name__ == "__main__":
    main()
