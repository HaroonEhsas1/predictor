# AMD Stock Prediction System - Advanced ML Trading Platform

A comprehensive AI-powered stock prediction system with advanced ML ensemble models, institutional data insights, multi-engine architecture, and automated trading signals for AMD stock predictions.

## 🎯 System Overview

This is an advanced trading system that combines multiple prediction engines:
- **After-Close Engine**: Predicts overnight gaps and next-day movements
- **Next-Day Predictor**: Advanced ensemble ML models for daily predictions
- **Intraday Engine**: Real-time 1-minute and 10-minute predictions
- **Institutional Insights**: Dark pool activity, options flow, and smart money tracking
- **SMS Notifications**: Twilio-powered real-time alerts

### Key Features

✅ **Multi-Engine Architecture**: Parallel prediction engines with ensemble models  
✅ **Institutional Intelligence**: Level 2 data, options flow, dark pool tracking  
✅ **Market State Detection**: Automatic weekend/holiday handling  
✅ **Data Integrity**: Multi-source fallback (Yahoo → Polygon → EODHD → Alpha Vantage)  
✅ **Advanced ML Models**: LightGBM, CatBoost, XGBoost, LSTM/GRU ensembles  
✅ **Risk Management**: Dynamic position sizing and confidence gating  
✅ **SMS Alerts**: Real-time trading signals via Twilio  
✅ **Database Persistence**: PostgreSQL with prediction history  
✅ **Clean API**: RESTful endpoints for integration  
✅ **CSV Logging**: Comprehensive prediction and performance tracking  

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher (recommended: 3.10+)
- **Operating System**: Linux, macOS, or Windows with WSL
- **RAM**: Minimum 4GB (8GB+ recommended for TensorFlow models)
- **Storage**: ~2GB for dependencies and models

---

## 🚀 Installation Guide

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-name>
```

### Step 2: Set Up Python Environment

**Option A: Using venv (Recommended)**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Option B: Using conda**
```bash
conda create -n stock-predictor python=3.10
conda activate stock-predictor
```

### Step 3: Install All Dependencies

#### Core Python Packages
```bash
pip install --upgrade pip

# Essential packages
pip install yfinance pandas numpy scikit-learn requests pytz python-dateutil

# Machine Learning Models
pip install lightgbm catboost xgboost

# Deep Learning (Optional - for LSTM/GRU models)
pip install tensorflow keras

# Web Framework (for API server)
pip install flask flask-cors

# Database
pip install psycopg2-binary peewee

# Twilio for SMS
pip install twilio

# Additional utilities
pip install colorlog scipy beautifulsoup4

# Reddit sentiment (optional)
pip install praw

# Economic data (optional)
pip install fredapi
```

#### Alternative: Install from requirements.txt
```bash
# If using the after_close_engine requirements
pip install -r engines/after_close_engine/requirements.txt

# Or create a complete requirements.txt with all packages
pip install -r requirements.txt
```

### Step 4: Environment Variables Setup

Create a `.env` file in the project root or export these variables:

```bash
# ====== ESSENTIAL API KEYS ======

# Data Sources (at least one recommended)
export POLYGON_API_KEY="your_polygon_api_key"          # Paid: $99/mo - Level 2 data, options flow
export ALPHA_VANTAGE_API_KEY="your_alpha_vantage_key"  # FREE tier available
export EODHD_API_KEY="your_eodhd_api_key"             # Alternative data source
export FINNHUB_API_KEY="your_finnhub_api_key"         # News & sentiment

# ====== NEW PREMIUM DATA SOURCES ======
export FMP_API_KEY="your_fmp_api_key"                 # Financial Modeling Prep - Fundamentals, analyst estimates
export MARKETAUX_API_KEY="your_marketaux_api_key"     # MarketAux - News sentiment with entity extraction

# ====== SMS NOTIFICATIONS (Twilio) ======
export TWILIO_ACCOUNT_SID="your_twilio_account_sid"
export TWILIO_AUTH_TOKEN="your_twilio_auth_token"
export TWILIO_PHONE_NUMBER="+1234567890"               # Your Twilio number
export SMS_ALERT_PHONE="+1234567890"                   # Recipient phone number

# ====== DATABASE (PostgreSQL) ======
export DATABASE_URL="postgresql://user:password@localhost:5432/stock_predictions"
export REPLIT_DATABASE_URL="your_replit_db_url"        # If using Replit

# ====== OPTIONAL ADVANCED APIS ======
export QUANDL_API_KEY="your_quandl_key"               # Economic data
export IEX_CLOUD_API_KEY="your_iex_cloud_key"         # Market data
export BENZINGA_API_KEY="your_benzinga_key"           # News sentiment
export CBOE_API_KEY="your_cboe_key"                   # Options data
export TD_AMERITRADE_API_KEY="your_td_key"            # Real-time quotes

# Reddit Sentiment (optional)
export REDDIT_CLIENT_ID="your_reddit_client_id"
export REDDIT_CLIENT_SECRET="your_reddit_secret"
export REDDIT_USERNAME="your_reddit_username"
export REDDIT_PASSWORD="your_reddit_password"

# Economic Data (optional)
export FRED_API_KEY="your_fred_api_key"               # Federal Reserve data
```

### Step 5: API Key Setup Guide

#### 🆓 Free Tier APIs (Start Here)

1. **Alpha Vantage** (FREE - 500 requests/day)
   - Sign up: https://www.alphavantage.co/support/#api-key
   - Use for: Options data, technical indicators, intraday prices

2. **Finnhub** (FREE tier available)
   - Sign up: https://finnhub.io/register
   - Use for: News sentiment, real-time quotes

3. **Financial Modeling Prep** (FREE - 250 requests/day)
   - Sign up: https://site.financialmodelingprep.com/developer/docs
   - Use for: Analyst estimates, price targets, earnings calendar, institutional ownership
   - Note: Free tier limited to 5 years of data; premium endpoints require paid plan

4. **MarketAux** (FREE - 100 requests/day)
   - Sign up: https://www.marketaux.com/
   - Use for: News sentiment with entity extraction, trending stocks analysis
   - Note: Some advanced endpoints (intraday stats) require paid plan

#### 💰 Premium APIs (High Value)

3. **Polygon.io** ($99/month - Recommended for serious trading)
   - Sign up: https://polygon.io/pricing
   - Provides: Level 2 data, institutional flow, real-time market data

4. **EODHD** (Varies by plan)
   - Sign up: https://eodhistoricaldata.com/pricing
   - Use for: EOD data, fundamentals, backup data source

#### 📱 Twilio SMS Setup (For Alerts)

5. **Twilio** (Pay-as-you-go, ~$0.0075/SMS)
   - Sign up: https://www.twilio.com/try-twilio
   - Get free trial credits
   - Set up phone number and API credentials

### Step 6: Database Setup

#### Option A: PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start PostgreSQL
sudo service postgresql start  # Linux
brew services start postgresql # macOS

# Create database
createdb stock_predictions

# Update DATABASE_URL in environment
export DATABASE_URL="postgresql://localhost:5432/stock_predictions"
```

#### Option B: Replit Database (Cloud)

If on Replit, database is auto-configured via `REPLIT_DATABASE_URL`.

### Step 7: Initialize Data Directories

```bash
# Create necessary directories
mkdir -p data/cache
mkdir -p data/predictions
mkdir -p data/nextday
mkdir -p logs
mkdir -p models
```

---

## ▶️ How to Run the System

### Main Prediction System

```bash
# Continuous mode (default) - runs every 10 minutes
python main.py --mode run --symbol AMD --interval 10

# Single prediction
python main.py --mode single --symbol AMD

# System test (verify installation)
python main.py --mode test

# Custom interval (5 minutes)
python main.py --mode run --symbol AMD --interval 5
```

### After-Close Engine (Overnight Gap Prediction)

```bash
# Navigate to engine directory
cd engines/after_close_engine

# Run prediction
python engine.py

# Train new models
python engine.py --train

# Start API server
python serve.py

# API will run on http://localhost:5050
```

#### After-Close Engine API Endpoints

```bash
# Get latest prediction
curl http://localhost:5050/after_close/prediction

# Health check
curl http://localhost:5050/health

# Engine status
curl http://localhost:5050/status
```

### Next-Day Prediction Engine

```bash
# Navigate to next-day engine
cd engines/nextday

# Generate prediction (dry-run mode)
python cli.py

# Train new models
python cli.py --train

# Enable/disable feature
python cli.py --enable
python cli.py --disable

# Set confidence threshold
python cli.py --confidence 0.85

# Set consensus threshold
python cli.py --consensus 0.80

# Specify model version
python cli.py --model-version v2.0

# Set lookback days for features
python cli.py --lookback-days 90

# Show system status
python cli.py --status

# Run unit tests
python cli.py --test
```

### Institutional Insights Engine

```bash
# Run institutional analysis
python professional_trader_system.py
```

### SMS Alert System

```bash
# Test SMS integration
python test_sms_integration.py

# Send custom alert
python sms_notifier.py
```

---

## 🏗️ Complete Project Structure

```
├── main.py                              # Main entry point
├── config.py                            # Global configuration
├── api_key_requirements.md              # Detailed API documentation
│
├── engine/                              # Core prediction engine
│   ├── __init__.py
│   ├── predictor.py                     # Main predictor class
│   ├── trainer.py                       # Model training
│   ├── ensemble_intraday.py             # Intraday ensemble models
│   ├── gap_nextday.py                   # Gap prediction logic
│   ├── feature_engineer.py              # Feature engineering
│   ├── data_collector.py                # Data collection
│   ├── logger.py                        # Logging utilities
│   └── visualizer.py                    # Visualization tools
│
├── engines/                             # Specialized engines
│   ├── after_close_engine/              # Overnight prediction
│   │   ├── engine.py                    # Main engine
│   │   ├── serve.py                     # API server
│   │   ├── config.py                    # Engine config
│   │   ├── fetchers.py                  # Data fetchers
│   │   ├── requirements.txt             # Dependencies
│   │   ├── data/predictions/            # Prediction storage
│   │   └── logs/                        # Engine logs
│   │
│   ├── nextday/                         # Next-day predictor
│   │   ├── cli.py                       # Command-line interface
│   │   ├── predict.py                   # Prediction logic
│   │   ├── config.py                    # Configuration
│   │   ├── data_ingest.py              # Data ingestion
│   │   ├── features.py                  # Feature engineering
│   │   ├── models.py                    # ML models
│   │   ├── gate.py                      # Prediction gating
│   │   └── README.md                    # Engine documentation
│   │
│   ├── institutional_insights_engine.py # Institutional data
│   ├── enhanced_confidence_gating.py    # Advanced gating
│   └── scalper_engine/                  # Scalping strategies
│
├── manager/                             # Orchestration
│   ├── scheduler.py                     # Market timing & sessions
│   └── resolve.py                       # Signal resolution
│
├── ui/                                  # User interface
│   └── printout.py                      # Console output formatting
│
├── sources/                             # Data sources
│   └── feeds.py                         # Multi-source data fetching
│
├── database/                            # Database layer
│   ├── prediction_database.py           # Database ORM
│   ├── prediction_schema.sql            # Schema definition
│   └── replit_database_bridge.py        # Replit integration
│
├── data/                                # Data storage
│   ├── cache/                           # Cached market data
│   ├── predictions/                     # Prediction archives
│   ├── nextday/                         # Next-day data
│   └── weekend/                         # Weekend data cache
│
├── logs/                                # Logging
│   ├── predictions.csv                  # Timestamped predictions
│   ├── errors.log                       # Error tracking
│   └── performance.log                  # Performance metrics
│
├── models/                              # Trained models
│   └── [auto-generated model files]
│
├── enhancements/                        # Additional features
│   └── reddit_sentiment.py              # Reddit sentiment analysis
│
├── archived_systems/                    # Legacy code
│   └── [previous versions]
│
├── sms_notifier.py                      # SMS alert system
├── professional_trader_system.py        # Institutional insights
├── local_transformer_sentiment.py       # Local sentiment analysis
├── ultra_accurate_gap_predictor.py      # Gap prediction
├── weekend_collector.py                 # Weekend data collection
└── README.md                            # This file
```

---

## ⚙️ Configuration

### Global Config (`config.py`)

Key settings you can adjust:

```python
# Trading thresholds
MIN_BACKTEST_ACCURACY = 0.60        # Minimum historical accuracy (60%)
MIN_ENSEMBLE_CONSENSUS = 0.80       # Minimum model agreement (80%)
MIN_EXPECTED_GAP = 1.50             # Minimum price movement ($1.50)

# Position sizing rules
POSITION_SIZES = {
    'low': 0.01,      # 1% for 70-75% consensus
    'medium': 0.03,   # 3% for 75-80% consensus
    'high': 0.07      # 7% for 80%+ consensus
}

# Market hours (Eastern Time)
MARKET_OPEN = "09:30"
MARKET_CLOSE = "16:00"
PRE_MARKET_START = "04:00"
AFTER_HOURS_END = "20:00"

# Data source priorities
DATA_SOURCES = ['yahoo', 'polygon', 'eodhd', 'alpha_vantage']
```

### After-Close Engine Config

Edit `engines/after_close_engine/config.py`:

```python
AFTER_CLOSE_ENABLED = True
CONFIDENCE_THRESHOLD = 0.80
SERVE_PORT = 5050
AUTO_FIT_ON_DEV = True              # Auto-train in dev mode
DEBUG_MODE = True
TIMEZONE = "US/Eastern"
```

### Next-Day Engine Config

Edit `engines/nextday/config.py`:

```python
CONFIG = {
    'enabled': True,
    'dry_run': True,                # Set False for live trading
    'min_confidence': 0.80,
    'min_ensemble_consensus': 0.80,
    'max_position_size': 0.07,      # 7% max
    'stop_loss_pct': 0.02,          # 2% stop loss
    'lookback_days': 60
}
```

---

## 🔌 API Documentation

### REST API Endpoints

#### After-Close Engine (`http://localhost:5050`)

**GET /after_close/prediction**
```bash
curl http://localhost:5050/after_close/prediction
```
Returns latest overnight gap prediction with confidence scores.

**GET /health**
```bash
curl http://localhost:5050/health
```
System health check.

**GET /status**
```bash
curl http://localhost:5050/status
```
Engine status and last run info.

### CLI Commands Reference

#### Main System
```bash
python main.py [OPTIONS]

Options:
  --mode {run|single|test}    Operation mode (default: run)
  --symbol SYMBOL             Stock symbol (default: AMD)
  --interval MINUTES          Update interval in minutes (default: 10)
```

#### Next-Day Engine
```bash
python engines/nextday/cli.py [OPTIONS]

Options:
  --train                     Train new models
  --predict                   Generate prediction (default)
  --status                    Show system status
  --enable                    Enable next-day prediction
  --disable                   Disable next-day prediction
  --dry-run BOOL             Enable/disable dry run (default: True)
  --confidence FLOAT         Set min confidence (default: 0.80)
  --consensus FLOAT          Set min consensus (default: 0.80)
  --model-version VERSION    Specify model version
  --lookback-days DAYS       Historical days for features (default: 60)
  --test                     Run unit tests
```

---

## 📊 Output Formats

### Console Output Example

```
🎯 AMD Stock Prediction System
===============================
📈 Target Stock: AMD
📍 Current Time: 15:52:00 EDT
📊 Market Status: MARKET_OPEN

✅ Data Quality: LIVE (Real-time sources)

🎯 PREDICTION (UNIFIED)
=======================================
📈 Direction: UP
💰 Target Price: $175.50
🔥 Signal Confidence: 85.3%
🤖 Ensemble Consensus: 82.5%
📊 Expected Gap: $2.15
⚖️ Risk Level: MEDIUM
📈 Backtest Accuracy: 64.2%

💼 TRADING DECISION
-------------------
🎯 Action: BUY
📊 Position Size: 7.0%
📋 Reason: All gates passed

🚪 Trading Gates:
   ✅ Live Trading: PASS
   ✅ Consensus: PASS (82.5% ≥ 80.0%)
   ✅ Gap Size: PASS ($2.15 ≥ $1.50)
   ✅ Market Open: PASS
   ✅ Backtest: PASS (64.2% ≥ 60%)
```

### CSV Logging (`logs/predictions.csv`)

```csv
utc_ts,et_ts,horizon,price_pred,direction,confidence,ensemble_consensus,expected_gap_usd,action,size,risk,backtest_acc,data_quality
2025-10-09T19:52:00Z,15:52:00 EDT,next_day,175.50,UP,0.853,0.825,2.15,BUY,0.07,MEDIUM,0.642,live
```

### JSON Output (`data/predictions/`)

```json
{
  "timestamp": "2025-10-09T15:52:00",
  "symbol": "AMD",
  "prediction": {
    "direction": "UP",
    "target_price": 175.50,
    "confidence": 0.853,
    "ensemble_consensus": 0.825,
    "expected_gap": 2.15
  },
  "trading_signal": {
    "action": "BUY",
    "position_size": 0.07,
    "risk_level": "MEDIUM"
  },
  "gates": {
    "backtest_accuracy": 0.642,
    "consensus_threshold": 0.80,
    "gap_threshold": 1.50,
    "all_passed": true
  }
}
```

---

## 🧪 Testing & Validation

### Run System Tests

```bash
# Full system test
python main.py --mode test

# Test next-day engine
cd engines/nextday
python cli.py --test

# Test SMS integration
python test_sms_integration.py

# Verify live data sources
python verify_live_data.py
```

### Manual Testing Checklist

- [ ] API keys are set correctly in environment
- [ ] Database connection is working
- [ ] Data sources return live data (not cached)
- [ ] SMS notifications send successfully
- [ ] Predictions are saved to CSV and database
- [ ] API endpoints respond correctly
- [ ] Models are loaded without errors

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Import Errors
```bash
# Error: No module named 'lightgbm'
pip install lightgbm catboost xgboost

# Error: No module named 'flask'
pip install flask flask-cors
```

#### 2. API Key Issues
```bash
# Check if keys are set
echo $POLYGON_API_KEY
echo $ALPHA_VANTAGE_API_KEY

# Test API connectivity
python verify_live_data.py
```

#### 3. Database Connection Errors
```bash
# Verify PostgreSQL is running
sudo service postgresql status

# Test connection
psql -d stock_predictions

# Reset database
dropdb stock_predictions
createdb stock_predictions
```

#### 4. "Possibly Delisted" Errors
- System automatically handles weekends/holidays
- Check if market is open using `python main.py --mode test`
- Verify data source fallback is working

#### 5. Weekend Mode Issues
- System auto-detects weekends and uses cached data
- No live trading signals on weekends (MONITOR only)
- Pre-populate weekend data: `python weekend_collector.py`

#### 6. SMS Not Sending
```bash
# Verify Twilio credentials
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN
echo $TWILIO_PHONE_NUMBER

# Test SMS
python test_sms_integration.py
```

#### 7. Model Training Failures
```bash
# Ensure enough historical data (60+ days)
# Check data quality
python verify_live_data.py

# Retrain models
cd engines/nextday
python cli.py --train
```

### Data Source Fallback Order

1. **Primary**: Yahoo Finance (real-time, free)
2. **Secondary**: Polygon.io (if API key set)
3. **Tertiary**: EODHD (if API key set)
4. **Fallback**: Alpha Vantage (if API key set)
5. **Cache**: Weekend/cached data (if market closed)

---

## 🖥️ Running on Local Machine (Cursor AI Setup)

### For Cursor AI or Local IDE

1. **Clone and Navigate**
   ```bash
   git clone <repo-url>
   cd <repo-name>
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r engines/after_close_engine/requirements.txt
   pip install twilio psycopg2-binary peewee tensorflow
   ```

4. **Configure Environment**
   Create `.env` file:
   ```bash
   # Copy all environment variables from "Environment Variables Setup" section above
   # At minimum, set:
   POLYGON_API_KEY=your_key
   ALPHA_VANTAGE_API_KEY=your_key
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=your_number
   ```

5. **Load Environment in Code**
   Add to your scripts:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Loads .env file
   ```

   Or use direnv:
   ```bash
   # Install direnv
   brew install direnv  # macOS
   apt install direnv   # Linux
   
   # Create .envrc
   echo "source .env" > .envrc
   direnv allow
   ```

6. **Initialize Directories**
   ```bash
   mkdir -p data/cache data/predictions data/nextday logs models
   ```

7. **Run System**
   ```bash
   # Test first
   python main.py --mode test
   
   # Run prediction
   python main.py --mode single --symbol AMD
   
   # Start continuous mode
   python main.py --mode run --symbol AMD --interval 10
   ```

### Cursor AI Specific Notes

- Cursor AI will understand the project structure from this README
- Use Cursor's AI to debug by referencing specific files
- Command palette: `Ctrl+Shift+P` → "Python: Select Interpreter" → choose `venv`
- Integrated terminal will use the venv automatically

---

## 📈 Trading Rules & Logic

### Gating Requirements

For any trade signal (BUY/SELL), **ALL** conditions must pass:

1. ✅ **Backtest Accuracy** ≥ 60%
2. ✅ **Ensemble Consensus** ≥ 80%
3. ✅ **Expected Gap** ≥ $1.50
4. ✅ **Market Open** (during trading hours)
5. ✅ **Data Quality** must be 'live' (not stale/cached)

### Position Sizing Logic

| Consensus Level | Position Size | Action    |
|----------------|---------------|-----------|
| < 70%          | 0%            | HOLD      |
| 70-75%         | 1%            | SMALL     |
| 75-80%         | 3%            | MEDIUM    |
| ≥ 80%          | 7%            | LARGE     |

### Risk Levels

- **LOW**: Consensus ≥ 85%, Confidence ≥ 85%
- **MEDIUM**: Consensus 75-85% OR Confidence 75-85%
- **HIGH**: Consensus < 75% OR Confidence < 75%

### Weekend/Holiday Behavior

- **Market Closed**: No trade signals (MONITOR only)
- **Weekend Mode**: Uses cached daily data
- **Pre-Market**: Can generate signals 30min before open
- **After-Hours**: Limited signals with reduced position size

---

## 📝 Development Guide

### Adding New Features

1. Update relevant config file (`config.py` or engine-specific)
2. Implement feature in appropriate module
3. Add tests: `python main.py --mode test`
4. Update this README with new functionality
5. Document API changes if applicable

### Logging Locations

- **Predictions**: `logs/predictions.csv`
- **Errors**: `logs/errors.log`
- **Performance**: `logs/performance.log`
- **Engine Logs**: `engines/*/logs/`
- **Database**: PostgreSQL or Replit DB

### Model Retraining

```bash
# Retrain all models
cd engines/nextday
python cli.py --train

# After-close engine auto-trains in dev mode
# Or manually:
cd engines/after_close_engine
python engine.py --train
```

---

## 🔐 Security Best Practices

1. **Never commit API keys** to git
2. Use `.env` file (add to `.gitignore`)
3. Rotate Twilio credentials regularly
4. Use read-only API keys where possible
5. Enable 2FA on all API provider accounts
6. Monitor API usage for anomalies
7. Set spending limits on paid APIs

---

## 📚 Additional Resources

### API Provider Documentation

- [Polygon.io Docs](https://polygon.io/docs)
- [Alpha Vantage Docs](https://www.alphavantage.co/documentation/)
- [Twilio Python SDK](https://www.twilio.com/docs/libraries/python)
- [Finnhub API](https://finnhub.io/docs/api)
- [EODHD API](https://eodhistoricaldata.com/financial-apis/)

### Machine Learning Resources

- [LightGBM Documentation](https://lightgbm.readthedocs.io/)
- [CatBoost Guide](https://catboost.ai/docs/)
- [TensorFlow Keras](https://www.tensorflow.org/guide/keras)
- [Scikit-learn](https://scikit-learn.org/stable/)

### Database Documentation

- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Peewee ORM](http://docs.peewee-orm.com/)

---

## 🆘 Support & Contact

For issues or questions:

1. Check `logs/` directory for error messages
2. Run system diagnostics: `python main.py --mode test`
3. Verify API keys: `python verify_live_data.py`
4. Review API quotas and limits
5. Check database connectivity

### Debugging Workflow

```bash
# 1. Test system health
python main.py --mode test

# 2. Verify data sources
python verify_live_data.py

# 3. Check engine status
cd engines/nextday
python cli.py --status

# 4. Review logs
tail -f logs/errors.log
tail -f logs/predictions.csv

# 5. Test individual components
python test_sms_integration.py
python professional_trader_system.py
```

---

## 📜 License

This project is for **educational and research purposes only**. 

**Disclaimer**: This software is not financial advice. Trading stocks involves risk. Always consult with a licensed financial advisor before making investment decisions.

---

## 🎉 Quick Start Summary

**Minimum Setup (5 minutes)**:

```bash
# 1. Install Python packages
pip install yfinance pandas numpy scikit-learn lightgbm requests pytz flask

# 2. Set at least one API key (FREE)
export ALPHA_VANTAGE_API_KEY="get_from_alphavantage.co"

# 3. Run test
python main.py --mode test

# 4. Generate prediction
python main.py --mode single --symbol AMD
```

**Full Setup (15 minutes)**:

```bash
# 1. Install all packages
pip install -r engines/after_close_engine/requirements.txt
pip install twilio psycopg2-binary tensorflow

# 2. Configure all environment variables (see .env section above)

# 3. Setup database
createdb stock_predictions

# 4. Initialize directories
mkdir -p data/cache data/predictions logs models

# 5. Run continuous mode
python main.py --mode run --symbol AMD --interval 10
```

---

**Last Updated**: October 9, 2025  
**Version**: 3.0  
**Maintainer**: Stock Prediction System Team
