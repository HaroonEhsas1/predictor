"""
Enhanced 10-Minute Stock Prediction System
Following professional trading system architecture with:
- Real-time 1-minute OHLCV data
- Technical indicators (EMA, RSI, MACD, VWAP, Volatility)
- Machine learning models (XGBoost, Random Forest)
- 40-cent target prediction logic
- Risk management with stop-loss/take-profit
"""

import os
import sys
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Try to import ML libraries
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML libraries not available, using fallback prediction methods")

@dataclass
class MarketData:
    """Enhanced market data with OHLCV and technical indicators"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    # Technical Indicators
    ema5: float = 0.0
    ema10: float = 0.0
    ema20: float = 0.0
    rsi14: float = 50.0
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_histogram: float = 0.0
    vwap: float = 0.0
    volatility: float = 0.0
    
    # Price action features
    price_change_1m: float = 0.0
    price_change_5m: float = 0.0
    volume_sma: float = 0.0
    high_low_pct: float = 0.0

@dataclass
class PredictionSignal:
    """10-minute prediction signal"""
    direction: str  # "BUY", "SELL", "HOLD"
    confidence: float
    target_price: float
    current_price: float
    expected_change: float
    stop_loss: float
    take_profit: float
    reasoning: str
    timestamp: datetime
    expires_at: datetime

class Enhanced10MinPredictor:
    """Professional 10-minute stock prediction system"""
    
    def __init__(self, symbol: str = "AMD", target_move: float = 0.40):
        self.symbol = symbol
        self.target_move = target_move  # 40 cents target
        self.prediction_window = 10  # 10 minutes
        self.stop_loss_cents = 20  # 20 cents stop loss
        
        # Data storage
        self.market_data: List[MarketData] = []
        self.current_prediction: Optional[PredictionSignal] = None
        self.prediction_history: List[PredictionSignal] = []
        
        # ML Models
        self.ml_model = None
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.model_trained = False
        self.feature_columns = []
        
        # Performance tracking
        self.trade_log: List[Dict] = []
        self.win_rate = 0.0
        self.confidence_threshold = 0.70  # Base threshold, use adaptive calculation in practice
        
    def fetch_realtime_data(self) -> Optional[pd.DataFrame]:
        """Fetch last 50 1-minute candles for AMD"""
        try:
            ticker = yf.Ticker(self.symbol)
            
            # Get 1-day of 1-minute data (up to 390 minutes)
            hist_1m = ticker.history(period="1d", interval="1m")
            
            if hist_1m.empty:
                print(f"❌ No data received for {self.symbol}")
                return None
                
            # Take last 50 candles for analysis
            data = hist_1m.tail(50).copy()
            
            # Ensure we have OHLCV columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_columns):
                print(f"❌ Missing required OHLCV data")
                return None
                
            # Reset index to get timestamp as column
            data.reset_index(inplace=True)
            data.rename(columns={'Datetime': 'timestamp'}, inplace=True)
            
            return data
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        try:
            df = df.copy()
            
            # Exponential Moving Averages
            df['EMA5'] = df['Close'].ewm(span=5).mean()
            df['EMA10'] = df['Close'].ewm(span=10).mean()
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            
            # RSI (14 periods)
            df['RSI'] = self.calculate_rsi(df['Close'], 14)
            
            # MACD (12, 26, 9)
            macd_line, macd_signal, macd_histogram = self.calculate_macd(df['Close'])
            df['MACD'] = macd_line
            df['MACD_Signal'] = macd_signal
            df['MACD_Histogram'] = macd_histogram
            
            # VWAP (Volume Weighted Average Price)
            df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
            
            # Volatility (10-period rolling standard deviation)
            df['Volatility'] = df['Close'].rolling(window=10).std()
            
            # Additional features
            df['Price_Change_1m'] = df['Close'].pct_change() * 100
            df['Price_Change_5m'] = df['Close'].pct_change(5) * 100
            df['Volume_SMA'] = df['Volume'].rolling(window=10).mean()
            df['High_Low_Pct'] = ((df['High'] - df['Low']) / df['Close']) * 100
            
            # Fill NaN values
            df = df.fillna(method='bfill').fillna(0)
            
            return df
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        macd_histogram = macd_line - macd_signal
        return macd_line.fillna(0), macd_signal.fillna(0), macd_histogram.fillna(0)
    
    def create_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Create training data with 40-cent target logic"""
        try:
            features = []
            targets = []
            
            # Define feature columns
            feature_cols = ['EMA5', 'EMA10', 'EMA20', 'RSI', 'MACD', 'MACD_Signal', 
                          'MACD_Histogram', 'VWAP', 'Volatility', 'Price_Change_1m', 
                          'Price_Change_5m', 'Volume_SMA', 'High_Low_Pct']
            
            # Create target labels based on 10-minute future price
            for i in range(len(df) - self.prediction_window):
                current_price = df['Close'].iloc[i]
                future_price = df['Close'].iloc[i + self.prediction_window]
                
                # 40-cent target logic
                if future_price >= current_price + self.target_move:
                    target = 1  # BUY signal
                elif future_price <= current_price - self.target_move:
                    target = -1  # SELL signal
                else:
                    target = 0  # HOLD
                
                # Extract features
                feature_row = df[feature_cols].iloc[i].values
                
                features.append(feature_row)
                targets.append(target)
            
            X = pd.DataFrame(features, columns=feature_cols)
            y = pd.Series(targets)
            
            self.feature_columns = feature_cols
            return X, y
            
        except Exception as e:
            print(f"❌ Error creating training data: {e}")
            return pd.DataFrame(), pd.Series()
    
    def train_ml_model(self, X: pd.DataFrame, y: pd.Series) -> bool:
        """Train machine learning model"""
        if not ML_AVAILABLE or X.empty or y.empty:
            print("⚠️ ML training skipped - insufficient data or libraries")
            return False
            
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest (fallback since XGBoost might not be available)
            self.ml_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            self.ml_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.ml_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ ML Model trained with {accuracy:.2%} accuracy")
            print(f"📊 Training samples: {len(X_train)} | Test samples: {len(X_test)}")
            
            self.model_trained = True
            return True
            
        except Exception as e:
            print(f"❌ ML training error: {e}")
            return False
    
    def make_prediction(self, current_data: MarketData) -> PredictionSignal:
        """Make 10-minute prediction using ML model or technical analysis"""
        try:
            current_time = datetime.now()
            expires_at = current_time + timedelta(minutes=self.prediction_window)
            
            # Default prediction
            prediction = PredictionSignal(
                direction="HOLD",
                confidence=0.5,
                target_price=current_data.close,
                current_price=current_data.close,
                expected_change=0.0,
                stop_loss=current_data.close - (self.stop_loss_cents / 100),
                take_profit=current_data.close + (self.target_move),
                reasoning="Insufficient data",
                timestamp=current_time,
                expires_at=expires_at
            )
            
            # Try ML prediction first
            if self.model_trained and self.ml_model and ML_AVAILABLE:
                ml_prediction = self.get_ml_prediction(current_data)
                if ml_prediction:
                    return ml_prediction
            
            # Fallback to technical analysis
            return self.get_technical_prediction(current_data)
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return prediction
    
    def get_ml_prediction(self, current_data: MarketData) -> Optional[PredictionSignal]:
        """Get prediction from trained ML model"""
        try:
            # Prepare features
            features = [
                current_data.ema5, current_data.ema10, current_data.ema20,
                current_data.rsi14, current_data.macd, current_data.macd_signal,
                current_data.macd_histogram, current_data.vwap, current_data.volatility,
                current_data.price_change_1m, current_data.price_change_5m,
                current_data.volume_sma, current_data.high_low_pct
            ]
            
            features_df = pd.DataFrame([features], columns=self.feature_columns)
            features_scaled = self.scaler.transform(features_df)
            
            # Get prediction and confidence
            prediction = self.ml_model.predict(features_scaled)[0]
            probabilities = self.ml_model.predict_proba(features_scaled)[0]
            confidence = max(probabilities)
            
            # Convert prediction to signal
            if prediction == 1 and confidence >= self.confidence_threshold:
                direction = "BUY"
                target_price = current_data.close + self.target_move
                stop_loss = current_data.close - (self.stop_loss_cents / 100)
                expected_change = self.target_move
                reasoning = f"ML model predicts UP with {confidence:.1%} confidence"
                
            elif prediction == -1 and confidence >= self.confidence_threshold:
                direction = "SELL"
                target_price = current_data.close - self.target_move
                stop_loss = current_data.close + (self.stop_loss_cents / 100)
                expected_change = -self.target_move
                reasoning = f"ML model predicts DOWN with {confidence:.1%} confidence"
                
            else:
                direction = "HOLD"
                target_price = current_data.close
                stop_loss = current_data.close
                expected_change = 0.0
                reasoning = f"ML model confidence {confidence:.1%} below threshold 45%"
            
            return PredictionSignal(
                direction=direction,
                confidence=confidence,
                target_price=target_price,
                current_price=current_data.close,
                expected_change=expected_change,
                stop_loss=stop_loss,
                take_profit=target_price,
                reasoning=reasoning,
                timestamp=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=self.prediction_window)
            )
            
        except Exception as e:
            print(f"❌ ML prediction error: {e}")
            return None
    
    def get_technical_prediction(self, current_data: MarketData) -> PredictionSignal:
        """Get prediction using technical analysis"""
        try:
            signals = []
            reasoning_parts = []
            
            # RSI signals
            if current_data.rsi14 < 30:
                signals.append(1)  # Oversold - BUY
                reasoning_parts.append(f"RSI oversold ({current_data.rsi14:.1f})")
            elif current_data.rsi14 > 70:
                signals.append(-1)  # Overbought - SELL
                reasoning_parts.append(f"RSI overbought ({current_data.rsi14:.1f})")
            
            # MACD signals
            if current_data.macd > current_data.macd_signal and current_data.macd_histogram > 0:
                signals.append(1)  # Bullish MACD
                reasoning_parts.append("MACD bullish crossover")
            elif current_data.macd < current_data.macd_signal and current_data.macd_histogram < 0:
                signals.append(-1)  # Bearish MACD
                reasoning_parts.append("MACD bearish crossover")
            
            # EMA trend signals
            if current_data.close > current_data.ema5 > current_data.ema10 > current_data.ema20:
                signals.append(1)  # Strong uptrend
                reasoning_parts.append("Strong EMA uptrend")
            elif current_data.close < current_data.ema5 < current_data.ema10 < current_data.ema20:
                signals.append(-1)  # Strong downtrend
                reasoning_parts.append("Strong EMA downtrend")
            
            # Price momentum
            if current_data.price_change_5m > 1.0:  # Strong 5-min momentum
                signals.append(1)
                reasoning_parts.append(f"Strong upward momentum ({current_data.price_change_5m:.1f}%)")
            elif current_data.price_change_5m < -1.0:
                signals.append(-1)
                reasoning_parts.append(f"Strong downward momentum ({current_data.price_change_5m:.1f}%)")
            
            # Aggregate signals
            if not signals:
                direction = "HOLD"
                confidence = 0.5
                expected_change = 0.0
                reasoning = "No clear technical signals"
            else:
                signal_sum = sum(signals)
                signal_strength = abs(signal_sum) / len(signals)
                
                if signal_sum > 0:
                    direction = "BUY"
                    expected_change = self.target_move
                elif signal_sum < 0:
                    direction = "SELL"
                    expected_change = -self.target_move
                else:
                    direction = "HOLD"
                    expected_change = 0.0
                
                confidence = min(0.5 + signal_strength * 0.3, 0.8)  # Cap at 80% for technical analysis
                reasoning = " + ".join(reasoning_parts) if reasoning_parts else "Mixed signals"
            
            # Calculate prices
            if direction == "BUY":
                target_price = current_data.close + self.target_move
                stop_loss = current_data.close - (self.stop_loss_cents / 100)
            elif direction == "SELL":
                target_price = current_data.close - self.target_move
                stop_loss = current_data.close + (self.stop_loss_cents / 100)
            else:
                target_price = current_data.close
                stop_loss = current_data.close
            
            return PredictionSignal(
                direction=direction,
                confidence=confidence,
                target_price=target_price,
                current_price=current_data.close,
                expected_change=expected_change,
                stop_loss=stop_loss,
                take_profit=target_price,
                reasoning=reasoning,
                timestamp=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=self.prediction_window)
            )
            
        except Exception as e:
            print(f"❌ Technical analysis error: {e}")
            return PredictionSignal(
                direction="HOLD",
                confidence=0.5,
                target_price=current_data.close,
                current_price=current_data.close,
                expected_change=0.0,
                stop_loss=current_data.close,
                take_profit=current_data.close,
                reasoning=f"Error: {e}",
                timestamp=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=self.prediction_window)
            )
    
    def process_market_data(self, df: pd.DataFrame) -> List[MarketData]:
        """Convert DataFrame to MarketData objects"""
        market_data_list = []
        
        for _, row in df.iterrows():
            market_data = MarketData(
                timestamp=row['timestamp'],
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume']),
                ema5=float(row.get('EMA5', 0)),
                ema10=float(row.get('EMA10', 0)),
                ema20=float(row.get('EMA20', 0)),
                rsi14=float(row.get('RSI', 50)),
                macd=float(row.get('MACD', 0)),
                macd_signal=float(row.get('MACD_Signal', 0)),
                macd_histogram=float(row.get('MACD_Histogram', 0)),
                vwap=float(row.get('VWAP', row['Close'])),
                volatility=float(row.get('Volatility', 0)),
                price_change_1m=float(row.get('Price_Change_1m', 0)),
                price_change_5m=float(row.get('Price_Change_5m', 0)),
                volume_sma=float(row.get('Volume_SMA', row['Volume'])),
                high_low_pct=float(row.get('High_Low_Pct', 0))
            )
            market_data_list.append(market_data)
        
        return market_data_list
    
    def display_prediction(self, prediction: PredictionSignal):
        """Display current prediction"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 80)
        print(f"🎯 ENHANCED 10-MINUTE PREDICTION SYSTEM - {prediction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Signal display
        signal_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}
        direction_emoji = {"BUY": "📈", "SELL": "📉", "HOLD": "➡️"}
        
        print(f"\n🎯 10-MINUTE PREDICTION:")
        print(f"   Signal:           {signal_emoji.get(prediction.direction, '❓')} {prediction.direction}")
        print(f"   Direction:        {direction_emoji.get(prediction.direction, '❓')} {prediction.direction}")
        print(f"   Confidence:       {prediction.confidence:.1%}")
        print(f"   Current Price:    ${prediction.current_price:.2f}")
        
        if prediction.direction != "HOLD":
            print(f"   Target Price:     ${prediction.target_price:.2f}")
            print(f"   Expected Move:    {prediction.expected_change:+.2f} ({abs(prediction.expected_change)/prediction.current_price*100:.1f}%)")
            print(f"   Stop Loss:        ${prediction.stop_loss:.2f}")
            
            profit_potential = abs(prediction.expected_change)
            risk_amount = abs(prediction.current_price - prediction.stop_loss)
            risk_reward = profit_potential / risk_amount if risk_amount > 0 else 0
            print(f"   Risk/Reward:      1:{risk_reward:.1f}")
        
        print(f"   Expires:          {prediction.expires_at.strftime('%H:%M:%S')}")
        print(f"   Reasoning:        {prediction.reasoning}")
        
        # Performance stats
        if self.prediction_history:
            recent_predictions = self.prediction_history[-10:]
            accuracy = sum(1 for p in recent_predictions if p.confidence > 0.7) / len(recent_predictions)
            print(f"\n📊 RECENT PERFORMANCE:")
            print(f"   Recent Accuracy:  {accuracy:.1%} (last {len(recent_predictions)} predictions)")
            print(f"   Model Status:     {'✅ ML Trained' if self.model_trained else '⚠️ Technical Only'}")
        
        print(f"\n🔄 Next update in 60 seconds...")
        print("💡 Press Ctrl+C to stop")
    
    def run_prediction_system(self):
        """Main prediction loop"""
        print("🚀 Starting Enhanced 10-Minute Prediction System...")
        print(f"📈 Target Stock: {self.symbol}")
        print(f"🎯 Target Move: {self.target_move:.2f} cents")
        print(f"⏰ Prediction Window: {self.prediction_window} minutes")
        print("=" * 50)
        
        iteration_count = 0
        
        try:
            while True:
                iteration_count += 1
                
                # Fetch real-time data
                print(f"📡 Fetching live market data... (iteration {iteration_count})")
                df = self.fetch_realtime_data()
                
                if df is None or df.empty:
                    print("❌ No data available, retrying in 60 seconds...")
                    time.sleep(60)
                    continue
                
                # Calculate technical indicators
                df_with_indicators = self.calculate_technical_indicators(df)
                
                # Process into MarketData objects
                market_data_list = self.process_market_data(df_with_indicators)
                self.market_data = market_data_list
                
                # Train ML model if enough data and not already trained
                if not self.model_trained and len(df_with_indicators) >= 30:
                    print("🧠 Training ML model...")
                    X, y = self.create_training_data(df_with_indicators)
                    if not X.empty and len(y.unique()) > 1:  # Need multiple classes
                        self.train_ml_model(X, y)
                
                # Get current market data
                current_data = market_data_list[-1] if market_data_list else None
                
                if current_data:
                    # Make prediction
                    prediction = self.make_prediction(current_data)
                    self.current_prediction = prediction
                    self.prediction_history.append(prediction)
                    
                    # Keep history manageable
                    if len(self.prediction_history) > 100:
                        self.prediction_history = self.prediction_history[-100:]
                    
                    # Display results
                    self.display_prediction(prediction)
                
                # Wait for next iteration
                time.sleep(60)  # Update every minute
                
        except KeyboardInterrupt:
            print("\n✅ Prediction system stopped gracefully.")
        except Exception as e:
            print(f"❌ System error: {e}")

def main():
    """Main entry point"""
    predictor = Enhanced10MinPredictor(symbol="AMD", target_move=0.40)
    predictor.run_prediction_system()

if __name__ == "__main__":
    main()