#!/usr/bin/env python3
"""
Verify LIVE data - fetch everything fresh right now
"""
import yfinance as yf
from datetime import datetime
import pytz
import requests

print("🔴 FETCHING LIVE DATA RIGHT NOW - NO CACHE")
print("=" * 80)

et_tz = pytz.timezone('US/Eastern')
now = datetime.now(et_tz)
print(f"⏰ Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print()

# 1. AMD Current Price (LIVE)
print("1️⃣ FETCHING LIVE AMD PRICE...")
amd = yf.Ticker('AMD')
amd_data = amd.history(period='1d', interval='1m')
if not amd_data.empty:
    amd_price = float(amd_data['Close'].iloc[-1])
    last_update = amd_data.index[-1]
    print(f"   💰 AMD: ${amd_price:.2f}")
    print(f"   ⏰ Last Update: {last_update}")
else:
    amd_price = 0
    print(f"   ⚠️ Market closed - using latest available")

# 2. Futures (LIVE)
print("\n2️⃣ FETCHING LIVE FUTURES DATA...")
futures = {
    'ES=F': 'S&P 500 Futures',
    'NQ=F': 'NASDAQ Futures',
    '^VIX': 'VIX'
}

futures_scores = []
for symbol, name in futures.items():
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='5d')
        if not data.empty and len(data) >= 2:
            current = float(data['Close'].iloc[-1])
            previous = float(data['Close'].iloc[-2])
            change_pct = ((current - previous) / previous) * 100
            futures_scores.append(change_pct)
            print(f"   📈 {name}: {change_pct:+.2f}%")
    except Exception as e:
        print(f"   ⚠️ {name}: Error - {e}")

futures_sentiment = sum(futures_scores) / len(futures_scores) * 0.3 if futures_scores else 0
print(f"   ➡️ Overall Futures Sentiment: {futures_sentiment:+.3f}")

# 3. Crypto (LIVE)
print("\n3️⃣ FETCHING LIVE CRYPTO DATA...")
crypto_symbols = ['BTC-USD', 'ETH-USD']
crypto_scores = []
for symbol in crypto_symbols:
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='3d')
        if not data.empty and len(data) >= 2:
            current = float(data['Close'].iloc[-1])
            previous = float(data['Close'].iloc[-2])
            change_pct = ((current - previous) / previous) * 100
            crypto_scores.append(change_pct)
            print(f"   ₿ {symbol}: {change_pct:+.2f}%")
    except Exception as e:
        print(f"   ⚠️ {symbol}: Error")

crypto_sentiment = sum(crypto_scores) / len(crypto_scores) * 0.1 if crypto_scores else 0
print(f"   ➡️ Overall Crypto Sentiment: {crypto_sentiment:+.3f}")

# 4. Semiconductor Sector (LIVE)
print("\n4️⃣ FETCHING LIVE SEMICONDUCTOR SECTOR DATA...")
sector_symbols = {
    'SOXX': 0.35,  # weight
    'SMH': 0.35,
    'NVDA': 0.20,
    'QQQ': 0.15
}

sector_scores = []
for symbol, weight in sector_symbols.items():
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='5d')
        if not data.empty and len(data) >= 2:
            current = float(data['Close'].iloc[-1])
            previous = float(data['Close'].iloc[-2])
            change_pct = ((current - previous) / previous) * 100
            weighted_score = change_pct * weight
            sector_scores.append(weighted_score)
            print(f"   🏭 {symbol}: {change_pct:+.2f}% (weight: {weight*100:.0f}%)")
    except Exception as e:
        print(f"   ⚠️ {symbol}: Error")

sector_sentiment = sum(sector_scores) if sector_scores else 0
print(f"   ➡️ Overall Sector Sentiment: {sector_sentiment:+.3f}%")

# 5. News Sentiment (LIVE)
print("\n5️⃣ FETCHING LIVE NEWS DATA...")
try:
    ticker = yf.Ticker('AMD')
    news = ticker.news
    if news:
        print(f"   📰 Found {len(news)} recent news articles")
        
        # Simple sentiment analysis on headlines
        bullish_keywords = ['surge', 'gain', 'rise', 'beat', 'strong', 'upgrade', 'buy', 'positive', 'growth']
        bearish_keywords = ['fall', 'drop', 'decline', 'miss', 'weak', 'downgrade', 'sell', 'negative', 'loss']
        
        sentiment_scores = []
        for article in news[:5]:
            title = article.get('title', '').lower()
            score = 0
            for word in bullish_keywords:
                if word in title:
                    score += 0.1
            for word in bearish_keywords:
                if word in title:
                    score -= 0.1
            sentiment_scores.append(score)
            print(f"   📄 {article.get('title', 'No title')[:60]}...")
        
        news_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        print(f"   ➡️ News Sentiment Score: {news_sentiment:+.3f}")
    else:
        news_sentiment = 0
        print(f"   ⚠️ No news available")
except Exception as e:
    news_sentiment = 0
    print(f"   ⚠️ News fetch error: {e}")

# CALCULATE FINAL SIGNAL
print("\n" + "=" * 80)
print("🎯 LIVE SIGNAL CALCULATION (JUST NOW)")
print("=" * 80)

overall = (news_sentiment * 0.50) + (futures_sentiment * 0.35) + (crypto_sentiment * 0.10) + (sector_sentiment * 0.05)

print(f"News (50%):     {news_sentiment:+.3f}")
print(f"Futures (35%):  {futures_sentiment:+.3f}")
print(f"Crypto (10%):   {crypto_sentiment:+.3f}")
print(f"Sector (5%):    {sector_sentiment:+.3f}")
print(f"─" * 80)
print(f"OVERALL:        {overall:+.3f}")

threshold = 0.08

if overall > threshold:
    signal = "🟢 BULLISH - BUY"
elif overall < -threshold:
    signal = "🔴 BEARISH - SELL"
else:
    signal = "⚪ NEUTRAL - HOLD"

print(f"Threshold:      ±{threshold}")
print(f"SIGNAL:         {signal}")
print(f"AMD Price:      ${amd_price:.2f}")
print("=" * 80)
print(f"⏰ Data fetched at: {datetime.now(et_tz).strftime('%H:%M:%S %Z')}")
