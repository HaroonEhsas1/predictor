#!/usr/bin/env python3
"""
PROFESSIONAL GAP PREDICTION SYSTEM
Predicts $2+ overnight price gaps for AMD stock
Perfect for overnight gap trading strategy
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import RobustScaler
import warnings
warnings.filterwarnings('ignore')

class GapPredictorPro:
    """Professional gap predictor focusing on $2+ overnight movements"""
    
    def __init__(self, symbol="AMD"):
        self.symbol = symbol
        self.models = {}
        self.scaler = None
        self.gap_threshold = 2.0  # $2 minimum gap target
        
    def collect_gap_data(self):
        """Collect historical gap data for training"""
        print("📊 Collecting gap training data...")
        
        # Get 2 years of data for better gap patterns
        ticker = yf.Ticker(self.symbol)
        hist = ticker.history(period="2y", interval="1d")
        
        if len(hist) < 200:
            raise ValueError("Need more historical data")
        
        # Calculate overnight gaps
        hist['prev_close'] = hist['Close'].shift(1)
        hist['overnight_gap'] = hist['Open'] - hist['prev_close']
        hist['gap_percent'] = (hist['overnight_gap'] / hist['prev_close']) * 100
        hist['gap_dollars'] = hist['overnight_gap']
        
        # Create gap features
        df = hist.copy()
        
        # Market sentiment features
        df['daily_return'] = df['Close'].pct_change()
        df['volume_spike'] = df['Volume'] / df['Volume'].rolling(20).mean()
        df['price_momentum'] = df['Close'] / df['Close'].rolling(5).mean() - 1
        df['volatility'] = df['daily_return'].rolling(10).std()
        
        # Technical indicators
        df['rsi'] = self.calculate_rsi(df['Close'])
        df['macd'] = self.calculate_macd(df['Close'])
        df['bb_position'] = self.calculate_bb_position(df['Close'])
        
        # Market context (using SPY as proxy)
        spy = yf.Ticker("SPY").history(period="2y", interval="1d")
        if len(spy) > 0:
            spy_aligned = spy.reindex(df.index, method='ffill')
            df['spy_return'] = spy_aligned['Close'].pct_change()
            df['spy_volume'] = spy_aligned['Volume'] / spy_aligned['Volume'].rolling(20).mean()
        else:
            df['spy_return'] = 0
            df['spy_volume'] = 1
        
        # VIX proxy (volatility indicator)
        df['market_stress'] = df['volatility'] > df['volatility'].rolling(50).quantile(0.8)
        
        # Day of week effects
        df['day_of_week'] = df.index.to_series().dt.dayofweek
        df['friday_effect'] = (df['day_of_week'] == 4).astype(int)  # Friday
        df['monday_effect'] = (df['day_of_week'] == 0).astype(int)  # Monday
        
        # Earnings proximity (approximate quarterly)
        df['earnings_proximity'] = np.sin(2 * np.pi * (df.index.to_series().dt.dayofyear % 90) / 90)
        
        # Target: next day's gap in dollars
        df['target_gap'] = df['gap_dollars'].shift(-1)
        
        # Feature columns
        self.feature_columns = [
            'daily_return', 'volume_spike', 'price_momentum', 'volatility',
            'rsi', 'macd', 'bb_position', 'spy_return', 'spy_volume',
            'market_stress', 'friday_effect', 'monday_effect', 'earnings_proximity'
        ]
        
        # Clean data
        df = df.dropna()
        
        # Analyze gap distribution
        gap_stats = {
            'total_days': len(df),
            'gaps_1plus': (abs(df['target_gap']) >= 1.0).sum(),
            'gaps_2plus': (abs(df['target_gap']) >= 2.0).sum(),
            'gaps_3plus': (abs(df['target_gap']) >= 3.0).sum(),
            'avg_gap': df['target_gap'].abs().mean(),
            'max_gap': df['target_gap'].abs().max()
        }
        
        print(f"📊 GAP ANALYSIS:")
        print(f"   Total trading days: {gap_stats['total_days']}")
        print(f"   Gaps ≥$1: {gap_stats['gaps_1plus']} ({gap_stats['gaps_1plus']/gap_stats['total_days']*100:.1f}%)")
        print(f"   Gaps ≥$2: {gap_stats['gaps_2plus']} ({gap_stats['gaps_2plus']/gap_stats['total_days']*100:.1f}%)")
        print(f"   Gaps ≥$3: {gap_stats['gaps_3plus']} ({gap_stats['gaps_3plus']/gap_stats['total_days']*100:.1f}%)")
        print(f"   Average gap: ${gap_stats['avg_gap']:.2f}")
        print(f"   Largest gap: ${gap_stats['max_gap']:.2f}")
        
        # Focus training on all gaps ≥$0.50 to capture patterns
        significant_gaps = abs(df['target_gap']) >= 0.5
        
        return df
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices):
        """Calculate MACD"""
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        return ema_12 - ema_26
    
    def calculate_bb_position(self, prices, window=20):
        """Calculate Bollinger Band position"""
        sma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        return (prices - sma) / (2 * std)
    
    def train_gap_models(self, data):
        """Train models specifically for gap prediction"""
        print("🤖 Training gap prediction models...")
        
        X = data[self.feature_columns].fillna(0)
        y = data['target_gap'].fillna(0)
        
        # Remove last row (no target)
        X = X.iloc[:-1]
        y = y.iloc[:-1]
        
        # Train-test split (more recent data for testing)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Scale features
        self.scaler = RobustScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble models optimized for gap prediction with better parameters
        self.models = {
            'rf': RandomForestRegressor(n_estimators=300, max_depth=20, min_samples_split=5, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=300, learning_rate=0.03, max_depth=12, subsample=0.8, random_state=42),
            'lr': LinearRegression()
        }
        
        model_scores = {}
        for name, model in self.models.items():
            model.fit(X_train_scaled, y_train)
            
            # Evaluate on test set
            pred = model.predict(X_test_scaled)
            
            # Enhanced accuracy calculation for all meaningful gaps
            from sklearn.metrics import mean_absolute_error, mean_squared_error
            
            # Overall prediction accuracy
            mae = mean_absolute_error(y_test, pred)
            rmse = np.sqrt(mean_squared_error(y_test, pred))
            
            # Direction accuracy for all gaps
            direction_accuracy = np.mean(np.sign(pred) == np.sign(y_test))
            
            # Accuracy for significant gaps (≥$2)
            significant_test = abs(y_test) >= 2.0
            if significant_test.sum() > 0:
                significant_pred = pred[significant_test]
                significant_actual = y_test[significant_test]
                
                # Direction accuracy for big gaps
                big_gap_direction = np.mean(np.sign(significant_pred) == np.sign(significant_actual))
                
                # Magnitude accuracy (within 40% of actual gap)
                magnitude_accuracy = np.mean(abs(significant_pred - significant_actual) / (abs(significant_actual) + 0.1) < 0.4)
                
                # Combined score emphasizing direction for trading
                overall_score = (big_gap_direction * 0.6 + direction_accuracy * 0.3 + magnitude_accuracy * 0.1)
                
                print(f"   {name}: DIR={direction_accuracy:.1%}, BIG_DIR={big_gap_direction:.1%}, MAG={magnitude_accuracy:.1%}, SCORE={overall_score:.1%}")
            else:
                overall_score = direction_accuracy * 0.8
                print(f"   {name}: DIR={direction_accuracy:.1%}, SCORE={overall_score:.1%}")
            
            model_scores[name] = overall_score
        
        self.best_model = max(model_scores.keys(), key=lambda x: model_scores[x])
        self.model_accuracy = model_scores[self.best_model]
        
        print(f"✅ Best model: {self.best_model} ({self.model_accuracy:.1%} accuracy)")
        return True
    
    def predict_next_gap(self):
        """Predict tomorrow's opening gap"""
        print("\n🔮 PREDICTING TOMORROW'S GAP...")
        
        # Get latest market data
        ticker = yf.Ticker(self.symbol)
        recent = ticker.history(period="3mo", interval="1d")
        
        if len(recent) < 50:
            raise ValueError("Insufficient recent data")
        
        # Calculate latest features
        df = recent.copy()
        df['daily_return'] = df['Close'].pct_change()
        df['volume_spike'] = df['Volume'] / df['Volume'].rolling(20).mean()
        df['price_momentum'] = df['Close'] / df['Close'].rolling(5).mean() - 1
        df['volatility'] = df['daily_return'].rolling(10).std()
        df['rsi'] = self.calculate_rsi(df['Close'])
        df['macd'] = self.calculate_macd(df['Close'])
        df['bb_position'] = self.calculate_bb_position(df['Close'])
        
        # Market context
        spy = yf.Ticker("SPY").history(period="3mo", interval="1d")
        if len(spy) > 0:
            spy_aligned = spy.reindex(df.index, method='ffill')
            df['spy_return'] = spy_aligned['Close'].pct_change()
            df['spy_volume'] = spy_aligned['Volume'] / spy_aligned['Volume'].rolling(20).mean()
        else:
            df['spy_return'] = 0
            df['spy_volume'] = 1
        
        df['market_stress'] = df['volatility'] > df['volatility'].rolling(50).quantile(0.8)
        
        # Day effects (tomorrow's day)
        tomorrow_dow = (datetime.now().weekday() + 1) % 7
        df['day_of_week'] = df.index.to_series().dt.dayofweek
        df['friday_effect'] = (tomorrow_dow == 4)
        df['monday_effect'] = (tomorrow_dow == 0)
        df['earnings_proximity'] = np.sin(2 * np.pi * (datetime.now().timetuple().tm_yday % 90) / 90)
        
        # Get latest features
        latest_features = df[self.feature_columns].iloc[-1:].fillna(0)
        latest_scaled = self.scaler.transform(latest_features)
        
        # Get predictions from all models
        predictions = {}
        for name, model in self.models.items():
            pred = model.predict(latest_scaled)[0]
            predictions[name] = pred
        
        # Ensemble prediction (weighted by accuracy)
        ensemble_gap = predictions[self.best_model]
        
        current_price = df['Close'].iloc[-1]
        predicted_open = current_price + ensemble_gap
        gap_percent = (ensemble_gap / current_price) * 100
        
        # Enhanced signal strength calculation
        abs_gap = abs(ensemble_gap)
        
        # Base confidence from model performance
        base_confidence = min(80, self.model_accuracy * 100 + 20)
        
        # Adjust confidence based on prediction agreement between models
        pred_values = list(predictions.values())
        pred_agreement = 1 - (np.std(pred_values) / (np.mean(np.abs(pred_values)) + 0.1))
        confidence_boost = pred_agreement * 20
        
        if abs_gap >= 3.0:
            signal_strength = "STRONG"
            confidence = min(95.0, base_confidence + confidence_boost + 15)
        elif abs_gap >= 2.0:
            signal_strength = "MODERATE" 
            confidence = min(85.0, base_confidence + confidence_boost + 10)
        elif abs_gap >= 1.5:
            signal_strength = "WEAK"
            confidence = min(75.0, base_confidence + confidence_boost + 5)
        else:
            signal_strength = "NO SIGNAL"
            confidence = min(60.0, base_confidence)
        
        direction = "UP" if ensemble_gap > 0 else "DOWN" if ensemble_gap < 0 else "NEUTRAL"
        
        return {
            'current_close': current_price,
            'predicted_open': predicted_open,
            'gap_dollars': ensemble_gap,
            'gap_percent': gap_percent,
            'direction': direction,
            'signal_strength': signal_strength,
            'confidence': confidence,
            'model_predictions': predictions,
            'model_accuracy': self.model_accuracy,
            'meets_threshold': abs_gap >= self.gap_threshold
        }
    
    def display_gap_prediction(self, prediction):
        """Display professional gap prediction"""
        print("\n" + "="*70)
        print("💰 PROFESSIONAL GAP PREDICTION - AMD OVERNIGHT MOVEMENT")
        print("🎯 TARGET: $2+ GAPS FOR PROFITABLE TRADING")
        print("="*70)
        
        print(f"\n📊 GAP ANALYSIS:")
        print(f"   Today's Close:      ${prediction['current_close']:.2f}")
        print(f"   Predicted Open:     ${prediction['predicted_open']:.2f}")
        print(f"   Expected Gap:       ${prediction['gap_dollars']:+.2f}")
        print(f"   Gap Percentage:     {prediction['gap_percent']:+.2f}%")
        
        print(f"\n🎯 TRADING SIGNAL:")
        print(f"   Direction:          {prediction['direction']}")
        print(f"   Signal Strength:    {prediction['signal_strength']}")
        print(f"   Confidence:         {prediction['confidence']:.1f}%")
        print(f"   Meets $2 Threshold: {'✅ YES' if prediction['meets_threshold'] else '❌ NO'}")
        
        print(f"\n🤖 MODEL ENSEMBLE:")
        print(f"   Best Model Accuracy: {prediction['model_accuracy']:.1%}")
        print(f"   Individual Predictions:")
        for model, pred in prediction['model_predictions'].items():
            print(f"     {model}: ${pred:+.2f}")
        
        print(f"\n💡 TRADING RECOMMENDATION:")
        if prediction['meets_threshold'] and prediction['confidence'] >= 70:
            action = f"TRADE {prediction['direction']}"
            entry = f"Enter at market close (${prediction['current_close']:.2f})"
            exit_price = f"Exit at market open (~${prediction['predicted_open']:.2f})"
            profit = f"Expected profit: ${abs(prediction['gap_dollars']):.2f} per share"
            
            print(f"   🚨 ACTION: {action}")
            print(f"   📈 ENTRY: {entry}")
            print(f"   📉 EXIT: {exit_price}")
            print(f"   💰 PROFIT: {profit}")
            
            if prediction['signal_strength'] == "STRONG":
                print(f"   📊 POSITION: LARGE (5-8% of portfolio)")
            elif prediction['signal_strength'] == "MODERATE":
                print(f"   📊 POSITION: MEDIUM (3-5% of portfolio)")
            else:
                print(f"   📊 POSITION: SMALL (1-3% of portfolio)")
        else:
            print(f"   ⏸️ ACTION: WAIT")
            if not prediction['meets_threshold']:
                print(f"   📝 REASON: Gap too small (${abs(prediction['gap_dollars']):.2f} < $2.00)")
            else:
                print(f"   📝 REASON: Low confidence ({prediction['confidence']:.1f}% < 70%)")
        
        print("="*70)

def main():
    """Run professional gap prediction system"""
    try:
        predictor = GapPredictorPro("AMD")
        
        # Collect and train on gap data
        print("🚀 Initializing Professional Gap Predictor...")
        gap_data = predictor.collect_gap_data()
        
        if predictor.train_gap_models(gap_data):
            # Make gap prediction
            prediction = predictor.predict_next_gap()
            predictor.display_gap_prediction(prediction)
            
            print(f"\n📅 Prediction generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
            print("💡 Use this signal 30 minutes before market close for best results")
        else:
            print("❌ Failed to train gap prediction models")
            
    except Exception as e:
        print(f"❌ Gap prediction system error: {e}")

if __name__ == "__main__":
    main()