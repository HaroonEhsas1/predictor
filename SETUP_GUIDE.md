# Quick Setup Guide for Local Machine

This guide will help you set up the AMD Stock Prediction System on your local machine (including Cursor AI).

## ⚡ Quick Start (5 Minutes)

### 1. Install Python 3.8+

Check your Python version:
```bash
python --version  # or python3 --version
```

If not installed, download from: https://www.python.org/downloads/

### 2. Clone Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 3. Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# Minimum required (FREE tier):
ALPHA_VANTAGE_API_KEY=your_key_here
```

Get free API key: https://www.alphavantage.co/support/#api-key

### 6. Test Installation

```bash
python main.py --mode test
```

### 7. Run Your First Prediction

```bash
python main.py --mode single --symbol AMD
```

---

## 🔑 API Keys Setup

### Free Tier (Start Here)

1. **Alpha Vantage** - FREE
   - Go to: https://www.alphavantage.co/support/#api-key
   - Enter email, get instant key
   - Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key`

2. **Finnhub** - FREE tier available
   - Go to: https://finnhub.io/register
   - Sign up, get API key
   - Add to `.env`: `FINNHUB_API_KEY=your_key`

### Premium (Optional - Better Data)

3. **Polygon.io** - $99/month (best for serious trading)
   - Go to: https://polygon.io/pricing
   - Choose "Stocks Starter" plan
   - Add to `.env`: `POLYGON_API_KEY=your_key`

### SMS Alerts (Optional)

4. **Twilio** - Pay-as-you-go (~$0.0075/SMS)
   - Go to: https://www.twilio.com/try-twilio
   - Get $15 free trial credits
   - Get Account SID, Auth Token, and Phone Number
   - Add to `.env`:
     ```
     TWILIO_ACCOUNT_SID=your_sid
     TWILIO_AUTH_TOKEN=your_token
     TWILIO_PHONE_NUMBER=+1234567890
     SMS_ALERT_PHONE=+1234567890
     ```

---

## 🗄️ Database Setup (Optional)

### Option 1: SQLite (Easiest - No Setup)
System will auto-create SQLite database in `data/` folder.

### Option 2: PostgreSQL (Recommended for Production)

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb stock_predictions
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
sudo -u postgres createdb stock_predictions
```

**Windows:**
1. Download from: https://www.postgresql.org/download/windows/
2. Install and start PostgreSQL
3. Use pgAdmin to create database `stock_predictions`

Update `.env`:
```bash
DATABASE_URL=postgresql://localhost:5432/stock_predictions
```

---

## 🎯 Running the System

### Main Prediction System

```bash
# Single prediction
python main.py --mode single --symbol AMD

# Continuous mode (every 10 minutes)
python main.py --mode run --symbol AMD --interval 10

# System test
python main.py --mode test
```

### After-Close Engine (Overnight Predictions)

```bash
cd engines/after_close_engine
python engine.py

# Start API server
python serve.py
# Access at: http://localhost:5050
```

### Next-Day Predictor

```bash
cd engines/nextday
python cli.py                    # Generate prediction
python cli.py --train            # Train models
python cli.py --status           # Check status
```

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: API Key Errors

**Solution:**
```bash
# Check if .env file exists
cat .env

# Verify variables are loaded
python -c "import os; print(os.getenv('ALPHA_VANTAGE_API_KEY'))"
```

If `None`, install python-dotenv:
```bash
pip install python-dotenv
```

Add to your Python scripts:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Issue: Database Connection Failed

**Solution:**
```bash
# Check PostgreSQL is running
sudo service postgresql status  # Linux
brew services list | grep postgresql  # Mac

# Test connection
psql -d stock_predictions
```

### Issue: No Predictions Generated

**Solution:**
1. Check market is open (9:30 AM - 4:00 PM ET)
2. Verify data source: `python verify_live_data.py`
3. Check logs: `cat logs/errors.log`

---

## 🖥️ Cursor AI Specific Setup

### 1. Open Project in Cursor

```bash
cursor .
```

Or: File → Open Folder → Select repository

### 2. Configure Python Interpreter

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter"
3. Choose `./venv/bin/python` (or `.\venv\Scripts\python.exe` on Windows)

### 3. Use Cursor AI

Now you can use Cursor's AI chat to:
- Debug errors by pasting error messages
- Ask about the codebase: "How does the after_close_engine work?"
- Request modifications: "Add error handling to main.py"
- Generate new features: "Create a function to send daily summaries"

Cursor will understand the project structure from the README.

### 4. Terminal in Cursor

Use integrated terminal (`` Ctrl+` ``), it will auto-activate venv:
```bash
python main.py --mode test
```

---

## 📝 Common Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# Install/Update packages
pip install -r requirements.txt
pip install <package-name>

# Run predictions
python main.py --mode single --symbol AMD

# Train models
cd engines/nextday
python cli.py --train

# Start API server
cd engines/after_close_engine
python serve.py

# View logs
tail -f logs/predictions.csv
tail -f logs/errors.log

# Test components
python main.py --mode test
python test_sms_integration.py
python verify_live_data.py
```

---

## 🔄 Updating the System

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Retrain models with new data
cd engines/nextday
python cli.py --train
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All packages installed (`pip list`)
- [ ] `.env` file created with at least ALPHA_VANTAGE_API_KEY
- [ ] Test runs successfully: `python main.py --mode test`
- [ ] Single prediction works: `python main.py --mode single --symbol AMD`
- [ ] Predictions saved to `logs/predictions.csv`
- [ ] No errors in `logs/errors.log`

---

## 🚀 Next Steps

Once setup is complete:

1. **Run a prediction**: `python main.py --mode single --symbol AMD`
2. **Check the output**: Look at console and `logs/predictions.csv`
3. **Explore the API**: `cd engines/after_close_engine && python serve.py`
4. **Train models**: `cd engines/nextday && python cli.py --train`
5. **Set up SMS alerts**: Add Twilio credentials to `.env`
6. **Schedule predictions**: Set up cron job or Task Scheduler

### Scheduling Predictions (Optional)

**Linux/Mac (cron):**
```bash
# Edit crontab
crontab -e

# Add line to run every hour during market hours
0 9-16 * * 1-5 cd /path/to/repo && /path/to/venv/bin/python main.py --mode single --symbol AMD
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start Program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `main.py --mode run --symbol AMD --interval 10`
7. Start in: `C:\path\to\repo`

---

## 📚 Additional Help

- **Full Documentation**: See `README.md`
- **API Documentation**: See `api_key_requirements.md`
- **Test Data Sources**: `python verify_live_data.py`
- **Debug SMS**: `python test_sms_integration.py`

---

**Setup complete!** 🎉

Now run: `python main.py --mode single --symbol AMD`
