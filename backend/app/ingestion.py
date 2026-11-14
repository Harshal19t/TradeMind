import os
import requests
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
USER_EMAIL = os.getenv("USER_EMAIL")

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

def fetch_news(ticker: str) -> str:
    url = "https://newsapi.org/v2/everything"
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    params = {
        "q": f"{ticker} stock OR earnings OR market",
        "from": from_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 10,
        "apiKey": NEWSAPI_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"Error fetching news: {response.status_code} - {response.text}"

    articles = response.json().get('articles', [])
    if not articles:
        return f"No recent news found for {ticker}"

    results = []  # ← list not string
    for article in articles[:5]:
        title = article.get('title', 'N/A')
        description = article.get('description', 'N/A')
        source = article.get('source', {}).get('name', 'N/A')
        published_at = article.get('publishedAt', '')[:10]

        results.append(
            f"Title: {title}\n"
            f"Source: {source}\n"
            f"Date: {published_at}\n"
            f"Summary: {description}\n"
        )

    return f"RECENT NEWS FOR {ticker}\n\n" + "\n---\n".join(results)

def fetch_filings(ticker: str) -> str:
    """Fetch latest SEC filing summary from EDGAR for a ticker."""
    # Get CIK number from ticker
    search_url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt=2024-01-01&forms=10-K,10-Q"
    headers = {"User-Agent": "TradeMind research@trademind.com"}

    try:
        # Look up CIK
        cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK={ticker}&type=10-Q&dateb=&owner=include&count=1&search_text=&action=getcompany&output=atom"
        cik_res = requests.get(cik_url, headers=headers, timeout=10)

        # Get recent filings via EDGAR full-text search
        search_res = requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&forms=10-Q&dateRange=custom&startdt=2024-01-01",
            headers=headers,
            timeout=10
        )

        if search_res.status_code != 200:
            return f"Could not fetch SEC filings for {ticker}"

        data = search_res.json()
        hits = data.get("hits", {}).get("hits", [])

        if not hits:
            return f"No recent SEC filings found for {ticker}"

        # Extract text snippets from top 3 filings
        texts = []
        for hit in hits[:3]:
            source = hit.get("_source", {})
            texts.append(f"""
            Filing: {source.get('form_type', 'N/A')}
            Date: {source.get('file_date', 'N/A')}
            Company: {source.get('display_names', 'N/A')}
            Extract: {source.get('period_of_report', 'N/A')}
            """)

        return f"SEC FILINGS FOR {ticker}\n" + "\n".join(texts)

    except Exception as e:
        return f"Error fetching SEC filings for {ticker}: {str(e)}"
    

def ingest_ticker(ticker: str) -> dict:
    ticker = ticker.upper().strip()
    print(f"Ingesting data for {ticker}...")

    price_text = fetch_price_data(ticker)
    filings_text = fetch_filings(ticker)
    news_text = fetch_news(ticker)

    return {
        "ticker": ticker,
        "price": price_text,
        "filings": filings_text,
        "news": news_text,
        "timestamp": datetime.now().isoformat(),
    }