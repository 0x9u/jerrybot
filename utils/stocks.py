import yfinance as yf

TOP_STOCKS =['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BRK-B', 'JNJ', 'V']

def get_top_stocks(period='1mo'):
    stock_data = []
    for ticker in TOP_STOCKS:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            # Calculate percentage change (latest close vs. start price)
            if len(hist) > 0:
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                pct_change = ((end_price - start_price) / start_price) * 100
                stock_data.append({'Ticker': ticker, 'Start Price': start_price, 
                                   'End Price': end_price, 'Change': pct_change})
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    return stock_data

# Retrieve data
