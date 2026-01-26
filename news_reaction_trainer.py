#!/usr/bin/env python3
"""Train headline->price-reaction models using Finnhub news and hourly price candles.

Usage:
    python news_reaction_trainer.py --stocks AMD,NVDA --days 30

Outputs:
    models/news_model_{SYMBOL}.joblib
"""
import os
import sys
import json
from datetime import datetime, timedelta
import time
import math
import requests
from pathlib import Path
import joblib
import argparse
from dotenv import load_dotenv
import yfinance as yf
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

load_dotenv()

# Download VADER lexicon if needed
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

FINNHUB = os.getenv('FINNHUB_API_KEY')

def fetch_finnhub_company_news(symbol, from_date, to_date):
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB}"
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        print(f"Finnhub error {r.status_code} for {symbol}: {r.text[:200]}")
        return []
    return r.json()

def fetch_hourly_candles(symbol, start_dt, end_dt):
    # Use yfinance hourly candles (60m)
    ticker = yf.Ticker(symbol)
    # period covers range; using start/end for reliability
    try:
        df = ticker.history(interval='60m', start=start_dt.strftime('%Y-%m-%d'), end=(end_dt + timedelta(days=1)).strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"yfinance error for {symbol}: {e}")
        return None

    if df.empty:
        return None

    df = df.reset_index()
    # Normalize Datetime to UTC tz-aware to allow comparisons with article timestamps
    try:
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        if df['Datetime'].dt.tz is None:
            df['Datetime'] = df['Datetime'].dt.tz_localize('UTC')
        else:
            df['Datetime'] = df['Datetime'].dt.tz_convert('UTC')
    except Exception:
        df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)

    return df

def align_article_to_hour(df_candles, article_ts):
    # article_ts is unix or ISO; convert to pandas.Timestamp
    if isinstance(article_ts, (int, float)):
        ts = pd.to_datetime(article_ts, unit='s', utc=True)
    else:
        ts = pd.to_datetime(article_ts)
        if ts.tzinfo is None:
            ts = ts.tz_localize('UTC')
        else:
            ts = ts.tz_convert('UTC')

    # Find the first candle whose Datetime >= article time
    df = df_candles.copy()
    # Ensure df has Datetime column in UTC
    if 'Datetime' not in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)
    else:
        if df['Datetime'].dt.tz is None:
            df['Datetime'] = df['Datetime'].dt.tz_localize('UTC')
        else:
            df['Datetime'] = df['Datetime'].dt.tz_convert('UTC')

    later = df[df['Datetime'] >= ts]
    if later.empty:
        return None
    return later.iloc[0]

def build_dataset_for_symbol(symbol, days=30, window_hours=1):
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=days)

    articles = fetch_finnhub_company_news(symbol, from_date.isoformat(), to_date.isoformat())
    if not articles:
        print(f"No articles for {symbol}")
        return None

    # Fetch hourly candles for the whole range
    candles = fetch_hourly_candles(symbol, from_date, to_date)
    if candles is None:
        print(f"No candles for {symbol}")
        return None

    rows = []
    for art in articles:
        try:
            ts = art.get('datetime') or art.get('time') or art.get('published')
            # Finnhub returns 'datetime' as unix seconds
            if ts is None:
                continue
            article_time = pd.to_datetime(int(ts), unit='s') if isinstance(ts, (int, float)) else pd.to_datetime(ts)

            # Align to hourly candle
            matched = align_article_to_hour(candles, article_time)
            if matched is None:
                continue

            entry_time = matched['Datetime']
            # find candle window_hours later
            later_time = entry_time + pd.Timedelta(hours=window_hours)
            later_candles = candles[candles['Datetime'] >= later_time]
            if later_candles.empty:
                continue
            later_candle = later_candles.iloc[0]

            price_before = float(matched['Close'])
            price_after = float(later_candle['Close'])
            ret = (price_after - price_before) / price_before

            # Label: up/down/neutral with small threshold
            thr = 0.002  # 0.2% 1-hour threshold
            if ret > thr:
                label = 'UP'
            elif ret < -thr:
                label = 'DOWN'
            else:
                label = 'NEUTRAL'

            text = (art.get('headline') or '') + ' ' + (art.get('summary') or '')
            if not text.strip():
                continue

            # VADER sentiment score for feature enrichment
            sia = SentimentIntensityAnalyzer()
            vader_scores = sia.polarity_scores(text)
            vader_compound = vader_scores['compound']

            rows.append({
                'text': text,
                'label': label,
                'article_time': str(article_time),
                'vader_compound': vader_compound,
                'source': art.get('source', 'unknown')
            })
        except Exception as e:
            print(f"Error processing article: {e}")
            continue

    df = pd.DataFrame(rows)
    return df

def train_and_save(df, symbol, out_dir='models'):
    os.makedirs(out_dir, exist_ok=True)
    X = df['text'].values
    y = df['label'].values

    if len(df) < 20:
        print(f"Not enough samples for {symbol}: {len(df)}")
        return False

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Use class_weight='balanced' to handle imbalanced classes better
    pipe = make_pipeline(
        TfidfVectorizer(max_features=5000, ngram_range=(1,2), min_df=2),
        LogisticRegression(max_iter=1000, class_weight='balanced')
    )
    pipe.fit(X_train, y_train)

    preds = pipe.predict(X_test)
    accuracy = (preds == y_test).mean()
    print(f"\n✅ Classification report for {symbol}:")
    print(f"   Test accuracy: {accuracy:.1%}")
    print(f"   Label distribution (train): {dict(zip(*np.unique(y_train, return_counts=True)))}")
    print(classification_report(y_test, preds, zero_division=0))

    joblib.dump(pipe, os.path.join(out_dir, f'news_model_{symbol}.joblib'))
    print(f"✅ Saved: {out_dir}/news_model_{symbol}.joblib")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stocks', type=str, default='AMD,NVDA,META,AVGO,SNOW,PLTR')
    parser.add_argument('--days', type=int, default=90)
    parser.add_argument('--window-hours', type=int, default=1)
    args = parser.parse_args()

    stocks = args.stocks.split(',')

    for s in stocks:
        print(f"\n=== Processing {s} ===")
        df = build_dataset_for_symbol(s, days=args.days, window_hours=args.window_hours)
        if df is None or df.empty:
            print(f"No training data for {s}")
            continue
        print(f"Collected {len(df)} labeled articles for {s}")
        train_and_save(df, s)
        # Be polite to APIs
        time.sleep(1)

if __name__ == '__main__':
    main()
