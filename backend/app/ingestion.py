import os
import requests
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def fetch_price_data(ticker: str) -> str:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="30d")
    info = stock.info
    if hist.empty:
        return f"No price data found for {ticker}."
    
    latest = hist.iloc[-1]
    previous = hist.iloc[-2]
    price_change = (latest['Close'] - previous['Close'])/previous['Close'] * 100
    
    pe_ratio = info.get('trailingPE', 'N/A')
    market_cap = info.get('marketCap', 'N/A')
    revenue = info.get('totalRevenue', 'N/A')
    profit_margin = info.get('profitMargins', 'N/A')
    week52_high = info.get('fiftyTwoWeekHigh', 'N/A')
    week52_low = info.get('fiftyTwoWeekLow', 'N/A')
    
    recent = hist.tail(5)[['Close', 'Volume']].to_string()
    
    result = f"""
    Price Data for {ticker}:
    Latest Close: {latest['Close']}
    Price Change (1 day): {price_change:.2f}%
    P/E Ratio: {pe_ratio}
    Market Cap: {market_cap}
    Revenue: {revenue}
    Profit Margin: {profit_margin}
    52 Week High: {week52_high}
    52 Week Low: {week52_low}
    Recent 5 Days:
    {recent}
    """
    
    return result