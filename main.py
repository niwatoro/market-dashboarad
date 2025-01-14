from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import yfinance as yf
from datetime import datetime, timedelta
from collections import defaultdict

app = FastAPI()

templates = Jinja2Templates(directory="templates")

ITEMS = [
    {"name": "日経平均", "ticker": "^N225", "category": "stock"},
    {"name": "NASDAQ", "ticker": "^IXIC", "category": "stock"},
    {"name": "USDJPY", "ticker": "JPY=X", "category": "currency"},
    {"name": "EURUSD", "ticker": "EURUSD=X", "category": "currency"},
    {"name": "米国債10年利回り", "ticker": "^TNX", "category": "rate"},
    {"name": "ビットコイン", "ticker": "BTC-USD", "category": "crypto"},
]

def fetch_data(ticker):
    try:
        data = yf.Ticker(ticker)
        history = data.history(period="5d")

        current_price = history["Close"].iloc[-1]

        change_percentage = (
            (current_price - history["Close"].iloc[0]) / history["Close"].iloc[0]
        ) * 100

        headlines = data.news[:3] if hasattr(data, "news") else []

        return {
            "current_price": current_price,
            "change_percentage": change_percentage,
            "headlines": headlines,
        }
    except Exception as error:
        raise ValueError(f"Unexpected {error=}; {ticker=}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    results = defaultdict(list)

    results["categories"] = list(set(item["category"] for item in ITEMS))

    for item in ITEMS:
        try:
            results[item["category"]].append(item | fetch_data(item["ticker"]))
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

    return templates.TemplateResponse("index.html", {"request": request, "results": results})

