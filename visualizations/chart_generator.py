#!/usr/bin/env python3
"""
Chart Generator Module
Creates professional matplotlib visualizations for predictions and performance
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import os
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ChartGenerator:
    """Professional chart generation for stock predictions"""
    
    def __init__(self, output_dir: str = 'visualizations/'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Chart styling
        self.colors = {
            'actual': '#2E86AB',
            'predicted': '#A23B72', 
            'confidence_high': '#F18F01',
            'confidence_low': '#C73E1D',
            'buy_signal': '#4CAF50',
            'sell_signal': '#F44336',
            'hold_signal': '#9E9E9E'
        }
        
    def create_prediction_performance_chart(self, predictions_df: pd.DataFrame, 
                                          actual_prices: pd.DataFrame,
                                          horizon: str = 'next_day') -> str:
        """
        Create predicted vs actual performance chart
        
        Args:
            predictions_df: DataFrame with columns ['timestamp', 'predicted_price', 'confidence', 'direction']
            actual_prices: DataFrame with columns ['timestamp', 'actual_price']
            horizon: Prediction horizon for title
            
        Returns:
            Filepath of saved chart
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
        
        # Merge data
        merged_df = pd.merge(predictions_df, actual_prices, on='timestamp', how='inner')
        if merged_df.empty:
            return None
        
        merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'])
        merged_df = merged_df.sort_values('timestamp')
        
        # Chart 1: Predicted vs Actual Prices
        ax1.plot(merged_df['timestamp'], merged_df['actual_price'], 
                label='Actual Price', color=self.colors['actual'], linewidth=2)
        ax1.scatter(merged_df['timestamp'], merged_df['predicted_price'], 
                   label='Predicted Price', color=self.colors['predicted'], alpha=0.7, s=50)
        
        ax1.set_title(f'{horizon.title()} Predictions vs Actual Prices', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Confidence Bands
        confidence_high = merged_df['confidence'] >= 0.8
        confidence_med = (merged_df['confidence'] >= 0.6) & (merged_df['confidence'] < 0.8)
        confidence_low = merged_df['confidence'] < 0.6
        
        ax2.scatter(merged_df[confidence_high]['timestamp'], 
                   merged_df[confidence_high]['confidence'],
                   label='High Confidence (≥80%)', color=self.colors['confidence_high'], s=60)
        ax2.scatter(merged_df[confidence_med]['timestamp'], 
                   merged_df[confidence_med]['confidence'],
                   label='Medium Confidence (60-80%)', color='orange', s=40)
        ax2.scatter(merged_df[confidence_low]['timestamp'], 
                   merged_df[confidence_low]['confidence'],
                   label='Low Confidence (<60%)', color=self.colors['confidence_low'], s=30)
        
        ax2.axhline(y=0.8, color='green', linestyle='--', alpha=0.7, label='Institutional Threshold')
        ax2.axhline(y=0.6, color='orange', linestyle='--', alpha=0.7, label='Minimum Threshold')
        
        ax2.set_title('Prediction Confidence Over Time', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Confidence', fontsize=12)
        ax2.set_ylim(0, 1)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Chart 3: Prediction Accuracy
        merged_df['prediction_error'] = abs(merged_df['predicted_price'] - merged_df['actual_price'])
        merged_df['error_pct'] = merged_df['prediction_error'] / merged_df['actual_price'] * 100
        
        # Rolling accuracy (percentage within 2% of actual)
        window = min(20, len(merged_df))
        merged_df['accurate_prediction'] = merged_df['error_pct'] < 2.0
        merged_df['rolling_accuracy'] = merged_df['accurate_prediction'].rolling(window=window).mean()
        
        ax3.plot(merged_df['timestamp'], merged_df['rolling_accuracy'] * 100, 
                color='green', linewidth=2, label=f'Rolling Accuracy ({window} periods)')
        ax3.axhline(y=60, color='red', linestyle='--', alpha=0.7, label='Minimum Acceptable (60%)')
        ax3.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='Institutional Grade (80%)')
        
        ax3.set_title('Prediction Accuracy Trend', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Accuracy (%)', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.set_ylim(0, 100)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Format x-axis for all subplots
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(merged_df)//10)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        filename = f'{horizon}_performance_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_intraday_signals_chart(self, price_data: pd.DataFrame, 
                                    signals: List[Dict[str, Any]],
                                    timeframe: str = '5m') -> str:
        """
        Create intraday chart with signals overlaid on candlesticks
        
        Args:
            price_data: OHLCV data
            signals: List of trading signals with timestamps
            timeframe: Data timeframe for title
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[3, 1])
        
        # Prepare data
        price_data['timestamp'] = pd.to_datetime(price_data.index)
        price_data = price_data.sort_values('timestamp')
        
        # Chart 1: Price with signals
        ax1.plot(price_data['timestamp'], price_data['Close'], 
                color='black', linewidth=1.5, label='Price')
        
        # Add moving averages
        if len(price_data) >= 20:
            price_data['SMA_20'] = price_data['Close'].rolling(20).mean()
            ax1.plot(price_data['timestamp'], price_data['SMA_20'], 
                    color='blue', alpha=0.7, label='SMA(20)')
        
        # Plot signals
        for signal in signals:
            timestamp = pd.to_datetime(signal['timestamp'])
            if timestamp in price_data['timestamp'].values:
                price_at_signal = price_data[price_data['timestamp'] == timestamp]['Close'].iloc[0]
                
                if signal['direction'] == 'BUY':
                    ax1.scatter(timestamp, price_at_signal, 
                              color=self.colors['buy_signal'], marker='^', 
                              s=100, label='Buy Signal', zorder=5)
                elif signal['direction'] == 'SELL':
                    ax1.scatter(timestamp, price_at_signal, 
                              color=self.colors['sell_signal'], marker='v', 
                              s=100, label='Sell Signal', zorder=5)
        
        ax1.set_title(f'AMD {timeframe} Price Action with Trading Signals', 
                     fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Volume
        ax2.bar(price_data['timestamp'], price_data['Volume'], 
               color='gray', alpha=0.6, width=0.0008)
        ax2.set_title('Volume', fontsize=12)
        ax2.set_ylabel('Volume', fontsize=10)
        ax2.set_xlabel('Time', fontsize=12)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        filename = f'intraday_signals_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_calibration_curve(self, calibrator, horizon: str) -> str:
        """Create calibration reliability diagram"""
        if not calibrator.calibration_curve_data:
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        curve_data = calibrator.calibration_curve_data
        
        # Chart 1: Reliability diagram
        ax1.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
        ax1.scatter(curve_data['bin_confidences'], curve_data['bin_accuracies'],
                   s=[c*10 for c in curve_data['bin_counts']], alpha=0.7, color='red')
        
        for i, (conf, acc, count) in enumerate(zip(curve_data['bin_confidences'], 
                                                   curve_data['bin_accuracies'],
                                                   curve_data['bin_counts'])):
            if count > 0:
                ax1.annotate(f'{count}', (conf, acc), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
        
        ax1.set_xlabel('Mean Predicted Probability')
        ax1.set_ylabel('Fraction of Positives')
        ax1.set_title(f'{horizon.title()} Calibration Curve')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Confidence distribution
        ax2.bar(range(len(curve_data['bin_centers'])), curve_data['bin_counts'],
               alpha=0.7, color='blue')
        ax2.set_xlabel('Confidence Bins')
        ax2.set_ylabel('Number of Predictions')
        ax2.set_title('Confidence Distribution')
        ax2.set_xticks(range(len(curve_data['bin_centers'])))
        ax2.set_xticklabels([f'{x:.1f}' for x in curve_data['bin_centers']], rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        filename = f'calibration_{horizon}_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_execution_summary_chart(self, execution_log: List[Dict[str, Any]]) -> str:
        """Create execution summary dashboard"""
        if not execution_log:
            return None
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        df = pd.DataFrame(execution_log)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Chart 1: Execution success rate
        df['executed'] = df['execute'].astype(int)
        success_rate = df['executed'].rolling(window=20).mean()
        
        ax1.plot(df['timestamp'], success_rate * 100, color='green', linewidth=2)
        ax1.axhline(y=20, color='red', linestyle='--', alpha=0.7, label='Target 20%+')
        ax1.set_title('Execution Success Rate (20-period rolling)')
        ax1.set_ylabel('Success Rate (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Position sizes
        executed_df = df[df['execute'] == True]
        if not executed_df.empty:
            ax2.scatter(executed_df['timestamp'], executed_df['position_size'] * 100,
                       c=executed_df['confidence'], cmap='RdYlGn', alpha=0.7)
            ax2.set_title('Position Sizes (Executed Trades)')
            ax2.set_ylabel('Position Size (%)')
            cbar = plt.colorbar(ax2.scatter(executed_df['timestamp'], executed_df['position_size'] * 100,
                                          c=executed_df['confidence'], cmap='RdYlGn', alpha=0.7), ax=ax2)
            cbar.set_label('Confidence')
        
        # Chart 3: Rejection reasons
        rejected_df = df[df['execute'] == False]
        if not rejected_df.empty:
            rejection_counts = rejected_df['stage_failed'].value_counts()
            ax3.pie(rejection_counts.values, labels=rejection_counts.index, autopct='%1.1f%%')
            ax3.set_title('Rejection Reasons')
        
        # Chart 4: Risk levels
        risk_counts = df['risk_level'].value_counts()
        colors_risk = {'LOW': 'green', 'MEDIUM': 'orange', 'HIGH': 'red'}
        ax4.bar(risk_counts.index, risk_counts.values, 
               color=[colors_risk.get(x, 'gray') for x in risk_counts.index])
        ax4.set_title('Risk Level Distribution')
        ax4.set_ylabel('Count')
        
        plt.tight_layout()
        
        # Save chart
        filename = f'execution_summary_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath

# Global chart generator
chart_generator = ChartGenerator()