# How to Run YOUR Ultra Accurate Gap Predictor

## 🎯 This is Your ACTUAL Production System

You're currently running the **Ultra Accurate Gap Predictor** - this is your professional institutional-grade system.

---

## ▶️ How to Run (Same as Replit)

### On Replit (Current):
```bash
python ultra_accurate_gap_predictor.py
```

### On Local Machine / Cursor AI (Identical):
```bash
# 1. Activate venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 2. Run the ultra accurate gap predictor
python ultra_accurate_gap_predictor.py
```

**That's it!** No `--mode` flags needed. This is a standalone system.

---

## 🏆 What This System Does

Based on your current logs, this system:

### 1. Data Collection (50+ Sources)
- ✅ Polygon.io (Level 2 data, options flow)
- ✅ Finnhub (real-time quotes, sentiment)
- ✅ EODHD (backup data)
- ✅ Alpha Vantage (technical indicators)
- ✅ FRED Economic Data
- ✅ Futures Markets (ES, NQ, RTY, Oil, Gold)
- ✅ Options Flow + Dark Pools
- ✅ News + Sentiment (multi-source)
- ✅ Insider Trading + Analyst Updates
- ✅ Global Markets + Currency
- ✅ Sector Rotation + ETF Flows

### 2. ML Predictions
- 🤖 Advanced ML Ensemble: LightGBM + CatBoost + LSTM/GRU
- 📊 Historical Data: 5+ years of data
- 🎯 Current Accuracy: **52.5%** live trading enabled
- 💪 Current Confidence: **89.0%** on predictions
- 📈 Target Prediction: UP $236.99 (from your latest run)

### 3. Trading Logic
- ✅ **Real-time collection** during market hours
- ✅ **Market close predictions** (locks at 4PM ET)
- ✅ **No prediction flips** - locked until next day
- ✅ **Position sizing**: Kelly-optimal (22.3% in latest)
- ✅ **Risk management**: LOW/MEDIUM/HIGH based on confidence

### 4. Notifications
- 📱 SMS alerts via Twilio
- 💾 Database persistence
- 📊 Daily prediction tracking
- 🔒 Prediction locking system

---

## 🔑 Required Environment Variables

Your system needs these keys (you already have them):

```bash
# Data Sources (You have these ✅)
POLYGON_API_KEY=<your_key>
ALPHA_VANTAGE_API_KEY=<your_key>
EODHD_API_KEY=<your_key>
FINNHUB_API_KEY=<your_key>

# SMS Notifications (You have these ✅)
TWILIO_ACCOUNT_SID=<your_sid>
TWILIO_AUTH_TOKEN=<your_token>
TWILIO_PHONE_NUMBER=<your_number>

# Reddit Sentiment (You have these ✅)
REDDIT_CLIENT_ID=<your_id>
REDDIT_CLIENT_SECRET=<your_secret>
REDDIT_USERNAME=<your_username>
REDDIT_PASSWORD=<your_password>

# Economic Data (You have this ✅)
FRED_API_KEY=<your_key>

# Database (You have this ✅)
DATABASE_URL=<your_db_url>
```

Copy all these from Replit to your local `.env` file.

---

## 📊 Current Performance (From Your Logs)

Your latest prediction:
```
🎯 Direction: UP
💰 Target: $236.99
🔥 Confidence: 89.0%
📊 Position Size: 22.3%
⚖️ Risk Level: LOW
✅ Quality Score: 75.0%
```

System accuracy:
```
📈 Historical accuracy: 52.5% (live trading enabled)
📊 Out-of-sample AMD accuracy: 63.9%
📈 Trained on 384 samples, tested on 97 unseen
```

---

## 🕐 How It Works (Timeline)

### Pre-Market (4:00 AM - 9:30 AM ET)
- 🔄 Continuous data collection
- 📊 Gathering institutional sources
- 💾 Caching for analysis

### Market Hours (9:30 AM - 4:00 PM ET)
- 📊 Real-time data collection
- 🏦 Institutional flow monitoring
- 💾 Building prediction dataset

### Market Close (4:00 PM ET)
- 🎯 **GENERATES PREDICTION** for next day
- 🔒 **LOCKS PREDICTION** (no changes allowed)
- 📱 Sends SMS notification
- 💾 Saves to database

### After-Hours (4:00 PM - 8:00 PM ET)
- 📊 Continued monitoring
- 🔒 Prediction remains locked
- ⏰ Waits for next market open

### Next Day
- 🔓 Unlocks at market close
- 🔄 Resets for new prediction cycle

---

## 🚀 Quick Setup on Local Machine

### Step 1: Install Dependencies
```bash
# Run setup script
./setup.sh  # Mac/Linux
setup.bat   # Windows

# Or manually
pip install -r requirements.txt
```

### Step 2: Copy Your API Keys
```bash
# In Replit, export keys:
env | grep -E "POLYGON|ALPHA|EODHD|FINNHUB|TWILIO|REDDIT|FRED|DATABASE" > my_keys.txt

# On local, create .env:
cp .env.example .env

# Paste all your keys into .env
nano .env  # or use Cursor editor
```

### Step 3: Run the System
```bash
# Activate environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run ultra accurate gap predictor
python ultra_accurate_gap_predictor.py
```

---

## 📝 What You'll See

When running, you'll see output like:

```
✅ Database bridge connection available
✅ Persistent prediction storage enabled (hybrid mode)
✅ SMS notifications enabled
🏛️ FRED Economic Data: ✅ Connected
📊 Data Sources: Polygon✅ | Finnhub✅ | Alpha Vantage✅ | EODHD✅
🚀 ULTRA ACCURATE GAP PREDICTOR: Starting PROFESSIONAL TRADER SYSTEM
📊 MARKET STATE: PRE_MARKET
🏦 INSTITUTIONAL DATA COLLECTOR: Gathering 50+ elite sources...
✅ Finnhub: Data acquired with price $235.56 | Quality: EXCELLENT (95/100)
📊 STAGE 1-2: Running two-stage institutional prediction...
✅ INSTITUTIONAL PREDICTION GENERATED
🎯 Direction: UP | Confidence: 89.0%
💰 Target: $236.99 | EV: 0.5%
📊 Position Size: 22.3% | Risk: LOW
🔒 PREDICTION LOCKED: UP (unbiased, allows NEUTRAL)
✅ AFTER-HOURS PREDICTION GENERATED & LOCKED!
```

---

## ⚠️ Important Notes

1. **Not the same as main.py**
   - `python ultra_accurate_gap_predictor.py` ← Your production system
   - `python main.py --mode run` ← Different, simpler system

2. **Runs continuously**
   - Keeps running and monitoring
   - Generates prediction at market close
   - Press Ctrl+C to stop

3. **Requires all API keys**
   - Needs Polygon, Finnhub, EODHD, FRED
   - Needs Twilio for SMS
   - Needs Reddit for sentiment
   - Copy ALL from Replit to local .env

4. **Database persistence**
   - Uses DATABASE_URL for storage
   - Can fallback to file-based if no DB
   - Predictions saved automatically

---

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "API key not found"
```bash
# Check .env file exists
cat .env

# Verify keys are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Polygon:', os.getenv('POLYGON_API_KEY')[:10] if os.getenv('POLYGON_API_KEY') else 'MISSING')"
```

### Issue: "Database connection error"
```bash
# Check DATABASE_URL is set
echo $DATABASE_URL

# System will fallback to file-based storage if DB unavailable
```

### Issue: No SMS notifications
```bash
# Check Twilio credentials
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN

# System will still run without SMS, just won't send alerts
```

---

## ✅ Verification

After starting, verify it's working:

1. **Check data collection:**
   - Should see "✅ Finnhub: Data acquired"
   - Should see "📊 Data Sources: Polygon✅"

2. **Check APIs connected:**
   - Should see "🏛️ FRED Economic Data: ✅ Connected"
   - Should see quality scores for data sources

3. **Check prediction generated:**
   - Should see "✅ INSTITUTIONAL PREDICTION GENERATED"
   - Should see Direction, Confidence, Target price

4. **Check SMS (optional):**
   - Should see SMS sent if phone configured
   - Or "⚠️ SMS_ALERT_PHONE environment variable not set"

---

## 🎯 Summary

**To run your Ultra Accurate Gap Predictor on local machine:**

```bash
# 1. Setup (one-time)
./setup.sh
cp .env.example .env
# Edit .env with your keys from Replit

# 2. Run (every time)
source venv/bin/activate
python ultra_accurate_gap_predictor.py
```

**That's your actual production system!** 🎉

---

## 📚 See Also

- **YOUR_SECRET_KEYS.md** - How to export your keys from Replit
- **LOCAL_SETUP_COMPLETE.md** - Full setup instructions
- **CURSOR_AI_GUIDE.md** - Using Cursor AI with this system
- **README.md** - Complete system documentation
