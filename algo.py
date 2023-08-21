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

    # Threshold to trigger buy or sell signal (e.g., 0.7 means 70% of total weight)
    threshold = 0.7

    # Continuous conditions
    buy_rsi = max(0, (30 - rsi) / 30)
    sell_rsi = max(0, (rsi - 70) / 30)
    buy_macd = max(0, min((macd - signal_line) / threshold, 1))
    sell_macd = max(0, min((signal_line - macd) / threshold, 1))
    buy_bollinger = max(0, min((lower_band - price) / threshold, 1))
    sell_bollinger = max(0, min((price - upper_band) / threshold, 1))

    # Weights for each indicator
    weight_rsi = 0.2
    weight_macd = 0.3
    weight_bollinger = 0.5
    total_weight = weight_rsi + weight_macd + weight_bollinger

    # Raw confidence levels
    raw_buy_confidence = buy_rsi * weight_rsi + buy_macd * weight_macd + buy_bollinger * weight_bollinger
    raw_sell_confidence = sell_rsi * weight_rsi + sell_macd * weight_macd + sell_bollinger * weight_bollinger

    # Normalized confidence levels
    buy_confidence = raw_buy_confidence / total_weight
    sell_confidence = raw_sell_confidence / total_weight

    return buy_confidence, sell_confidence

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

def backtest(tickers, start_date, end_date, initial_balance=100000, TRANSACTION_COST_PERCENTAGE=0.001, SLIPPAGE_PERCENTAGE=0.002):
    balance = initial_balance
    portfolio = {}

    def apply_transaction_cost(amount):
        return amount * (1 - TRANSACTION_COST_PERCENTAGE)

    def apply_slippage(price, is_buy):
        return price * (1 + SLIPPAGE_PERCENTAGE) if is_buy else price * (1 - SLIPPAGE_PERCENTAGE)

    for ticker in tickers:
        data = get_data(ticker, start_date, end_date) # Function to fetch data for the ticker
        buy_confidences, sell_confidences = indicator_function(data) # Function to calculate buy/sell confidence

        for date, buy_confidence in buy_confidences.iterrows():
            if buy_confidence > 0:
                investment = balance * buy_confidence
                buy_price = apply_slippage(data['price'][date], is_buy=True)
                shares_to_buy = investment // buy_price
                cost = shares_to_buy * buy_price
                balance -= apply_transaction_cost(cost)
                portfolio[ticker] = shares_to_buy

        for date, sell_confidence in sell_confidences.iterrows():
            if sell_confidence > 0 and ticker in portfolio:
                sell_price = apply_slippage(data['price'][date], is_buy=False)
                revenue = portfolio[ticker] * sell_price
                balance += apply_transaction_cost(revenue)
                del portfolio[ticker]

    # Final valuation of the portfolio
    for ticker, shares in portfolio.items():
        balance += shares * get_data(ticker, end_date, end_date)['price'][0] # Assuming get_data returns price for the date

    return balance

def get_stocks_to_watch(volume_min=1000000, volume_max=10000000, pe_min=10, pe_max=30, dividend_yield_min=0.01):
    # Get a broad list of tickers (e.g., S&P 500, NASDAQ 100, etc.)
    tickers_to_consider = yf.Ticker("^GSPC").history(period="1d").index

    stocks_to_watch = {}
    for ticker_symbol in tickers_to_consider:
        ticker = yf.Ticker(ticker_symbol)
        
        # Fetch stock information
        stock_info = ticker.info

        # Check trading volume
        if volume_min <= stock_info.get('averageVolume', 0) <= volume_max:
            # Check price-to-earnings ratio
            if pe_min <= stock_info.get('trailingPE', 0) <= pe_max:
                # Check dividend yield
                if stock_info.get('dividendYield', 0) >= dividend_yield_min:
                    # Additional criteria can be added here
                    stocks_to_watch[stock_info['longName']] = stock_info['symbol']

    return stocks_to_watch

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