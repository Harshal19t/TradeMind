from app.ingestion import ingest_ticker

data = ingest_ticker("AAPL")
print(data["price"])
print("---")
print(data["news"])