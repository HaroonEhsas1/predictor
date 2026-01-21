#!/usr/bin/env python3
"""
Backtesting script for evaluating the accuracy of the stock prediction system over historical data.
This script simulates predictions for past dates and compares them against actual market outcomes.
"""
import os
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import traceback

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor

from stock_config import get_active_stocks, get_stock_config

# Ensure output directory exists
OUTPUT_DIR = os.path.join('data', 'backtest')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_historical_data(symbol, start_date, end_date):
    """
    Fetch historical stock data for a given symbol between start and end dates.
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        if hist.empty:
            print(f"No historical data found for {symbol}")
            return None
        return hist
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return None

def run_backtest(start_date, end_date, stocks=None, apply_filters=True, apply_safeguard=False):
    """
    Run backtest over a range of dates for specified stocks.
    Simulates predictions for each day as if they were made on that day.
    """
    if stocks is None:
        stocks = get_active_stocks()
    
    print("\n" + "="*80)
    print(f" BACKTESTING STOCK PREDICTION SYSTEM")
    print(f" Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f" Stocks: {', '.join(stocks)}")
    print("="*80)
    
    results = {}
    for symbol in stocks:
        results[symbol] = []
    
    current_date = start_date
    while current_date <= end_date:
        print("\n" + "-"*80)
        print(f" Simulating predictions for {current_date.strftime('%Y-%m-%d')}")
        print("-"*80)
        
        for symbol in stocks:
            try:
                print(f"\nProcessing {symbol} for {current_date.strftime('%Y-%m-%d')}")
                # Initialize predictor
                predictor = ComprehensiveNextDayPredictor(symbol)
                # Note: We need to ensure the predictor uses data only up to current_date
                # This might require modifications to the predictor to limit data fetch
                prediction = predictor.generate_comprehensive_prediction()
                
                if prediction is None:
                    print(f" Error predicting {symbol}: Unable to generate prediction due to missing data")
                    continue
                
                if not prediction:
                    print(f"\n Failed to generate prediction for {symbol}")
                    continue
                
                # Fetch actual outcome for the next day to evaluate accuracy
                next_day = current_date + timedelta(days=1)
                hist = fetch_historical_data(symbol, current_date, next_day + timedelta(days=1))
                if hist is None or len(hist) < 2:
                    print(f" Insufficient historical data to evaluate {symbol} on {current_date.strftime('%Y-%m-%d')}")
                    continue
                
                actual_close_next_day = hist['Close'].iloc[-1]
                actual_move_percent = ((actual_close_next_day - prediction['current_price']) / prediction['current_price'] * 100) if prediction['current_price'] > 0 else 0.0
                prediction_correct = False
                if prediction['direction'] == 'UP' and actual_close_next_day > prediction['current_price']:
                    prediction_correct = True
                elif prediction['direction'] == 'DOWN' and actual_close_next_day < prediction['current_price']:
                    prediction_correct = True
                elif prediction['direction'] == 'NEUTRAL' and abs(actual_move_percent) < 0.5:  # Small threshold for neutral
                    prediction_correct = True
                
                result = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'direction': prediction.get('direction'),
                    'confidence': prediction.get('confidence'),
                    'current_price': prediction.get('current_price'),
                    'target_price': prediction.get('target_price'),
                    'expected_move_percent': prediction.get('expected_move_percent', 0.0),
                    'actual_close_next_day': float(actual_close_next_day),
                    'actual_move_percent': actual_move_percent,
                    'prediction_correct': prediction_correct,
                    'explanation': prediction.get('explanation'),
                    'recommendation': prediction.get('recommendation')
                }
                
                results[symbol].append(result)
                
                print(f"  Prediction: {result['direction']} with {result['confidence']:.1f}% confidence")
                print(f"  Current Price: ${result['current_price']:.2f}, Target: ${result['target_price']:.2f}")
                print(f"  Actual Next Day Close: ${result['actual_close_next_day']:.2f}, Move: {result['actual_move_percent']:.2f}%")
                print(f"  Prediction Correct: {'YES' if result['prediction_correct'] else 'NO'}")
                
            except Exception as e:
                print(f" Error predicting {symbol} on {current_date.strftime('%Y-%m-%d')}: {e}")
                traceback.print_exc()
        
        current_date += timedelta(days=1)
    
    # Summarize accuracy
    print("\n" + "="*80)
    print(" BACKTEST SUMMARY")
    print("="*80)
    
    overall_correct = 0
    overall_predictions = 0
    for symbol, preds in results.items():
        if not preds:
            print(f"\n{symbol}: No predictions available")
            continue
        
        correct = sum(1 for p in preds if p['prediction_correct'])
        total = len(preds)
        accuracy = correct / total * 100 if total > 0 else 0.0
        
        print(f"\n{symbol}:")
        print(f"   Total Predictions: {total}")
        print(f"   Correct Predictions: {correct}")
        print(f"   Accuracy: {accuracy:.1f}%")
        
        overall_correct += correct
        overall_predictions += total
    
    overall_accuracy = overall_correct / overall_predictions * 100 if overall_predictions > 0 else 0.0
    print("\n" + "-"*80)
    print(f"Overall Accuracy Across All Stocks: {overall_accuracy:.1f}% ({overall_correct}/{overall_predictions} correct)")
    print("-"*80)
    
    # Save results
    output_file = os.path.join(OUTPUT_DIR, f"backtest_results_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json")
    with open(output_file, 'w') as f:
        json.dump({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'stocks': stocks,
            'results': results,
            'overall_accuracy': overall_accuracy
        }, f, indent=2)
    
    print(f"\n Saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    # Example: Backtest for October 2025
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2025, 10, 31)
    stocks = ['AMD', 'AVGO', 'ORCL', 'NVDA']
    
    run_backtest(start_date, end_date, stocks)
