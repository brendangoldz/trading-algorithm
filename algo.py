import yfinance as yf
from datetime import datetime, timedelta

def get_data(ticker):
    # Get today's date and a year before today's date
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

    # Fetch the historical data for the given ticker
    stock_data = yf.Ticker(ticker)
    data = stock_data.history(period='1d', start=start_date, end=end_date)

    # Calculate Bollinger Bands
    data['mid band'] = data['Close'].rolling(window=20).mean()
    data['std'] = data['Close'].rolling(window=20).std()
    data['upper band'] = data['mid band'] + (data['std'] * 2)
    data['lower band'] = data['mid band'] - (data['std'] * 2)
    data['price'] = data['Close']

    return data

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['price'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['price'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal_line

def calculate_rsi(data, window=14):
    delta = data['price'].diff(1)
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def indicator_function(data):
    # Calculate RSI
    rsi = calculate_rsi(data)
    # Calculate MACD and Signal Line
    macd, signal_line = calculate_macd(data)
    # Bollinger Bands (Assuming you have these calculated in 'data')
    upper_band = data['upper band']
    lower_band = data['lower band']
    price = data['price']

    # Weights for each indicator
    weight_rsi = 0.2
    weight_macd = 0.3
    weight_bollinger = 0.5

    # Buy Condition
    buy_rsi = (rsi < 30) * weight_rsi
    buy_macd = (macd > signal_line) * weight_macd
    buy_bollinger = (price < lower_band) * weight_bollinger
    buy_condition = buy_rsi + buy_macd + buy_bollinger

    # Sell Condition
    sell_rsi = (rsi > 70) * weight_rsi
    sell_macd = (macd < signal_line) * weight_macd
    sell_bollinger = (price > upper_band) * weight_bollinger
    sell_condition = sell_rsi + sell_macd + sell_bollinger

    # Threshold to trigger buy or sell signal (e.g., 0.7 means 70% of total weight)
    threshold = 0.7

    return buy_condition > threshold, sell_condition > threshold

def assess_stocks(tickers):
    for ticker in tickers:
        # Assuming you have a function to get the data for the given ticker
        data = get_data(ticker)
        buy, sell = indicator_function(data)
        if buy:
            print(f"Buy signal for {ticker}")
        elif sell:
            print(f"Sell signal for {ticker}")
        else:
            print(f"No signal for {ticker}")

stocks_dict = {
    "PubMatic": "PUBM",
    "Endava": "DAVA",
    "Sprout Social": "SPT",
    "Yeti Holdings": "YETI",
    "Alpha Metallurgical Resources": "AMR",
    "Aspen Technology": "AZPN",
    "e.l.f. Beauty": "ELF",
    "Global-E Online": "GLBE",
    "Boeing": "BA",
    "Southwest Airlines": "LUV",
    "iRobot": "IRBT",
    "SPDR Portfolio S&P 500 Growth ETF": "SPYG"
}

tickers_array = list(stocks_dict.values())

# Call the main function with the tickers array
assess_stocks(tickers_array)