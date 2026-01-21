# Complete Local Setup Instructions for Cursor AI

## 🎯 Overview

This system is currently running on Replit. Here's EXACTLY how to transfer it to your local machine and run it in Cursor AI.

---

## 📦 What Cursor AI Needs to Install

Yes, Cursor AI (and your local machine) need to install all Python packages first. The setup script handles this automatically.

### Automated Setup (Recommended)

**Mac/Linux:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

This installs:
- ✅ All Python packages (pandas, numpy, scikit-learn, lightgbm, catboost, xgboost, tensorflow, etc.)
- ✅ Web framework (Flask)
- ✅ Database drivers (psycopg2, peewee)
- ✅ Twilio for SMS
- ✅ Reddit API client (praw)
- ✅ All other dependencies

### Manual Installation (Alternative)

If setup script doesn't work:

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install all packages
pip install -r requirements.txt
```

---

## 🔑 Your Secret Keys - MUST Transfer

You have these keys configured in Replit that MUST be copied to local `.env`:

### Quick Export from Replit

**Run this command in Replit Shell:**

```bash
echo "Copy these to your local .env file:"
echo ""
env | grep -E "POLYGON_API_KEY|ALPHA_VANTAGE_API_KEY|EODHD_API_KEY|FINNHUB_API_KEY|TWILIO|REDDIT|FRED_API_KEY|DATABASE_URL" | sort
```

### Then on Local Machine

1. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Paste all the keys from Replit into `.env`

3. Your `.env` should have:
   ```bash
   POLYGON_API_KEY=<from_replit>
   ALPHA_VANTAGE_API_KEY=<from_replit>
   EODHD_API_KEY=<from_replit>
   FINNHUB_API_KEY=<from_replit>
   TWILIO_ACCOUNT_SID=<from_replit>
   TWILIO_AUTH_TOKEN=<from_replit>
   TWILIO_PHONE_NUMBER=<from_replit>
   REDDIT_CLIENT_ID=<from_replit>
   REDDIT_CLIENT_SECRET=<from_replit>
   REDDIT_USERNAME=<from_replit>
   REDDIT_PASSWORD=<from_replit>
   FRED_API_KEY=<from_replit>
   DATABASE_URL=<from_replit>
   ```

See `YOUR_SECRET_KEYS.md` for detailed instructions.

---

## ▶️ How to Run (Same as Replit)

Once setup is complete, run the same way as in Replit:

### 1. Main Prediction System

```bash
# Single prediction (same as Replit)
python main.py --mode single --symbol AMD

# Continuous mode (same as Replit)
python main.py --mode run --symbol AMD --interval 10

# System test
python main.py --mode test
```

### 2. After-Close Engine

```bash
# Navigate to engine
cd engines/after_close_engine

# Run prediction (same as Replit)
python engine.py

# Start API server (same as Replit)
python serve.py
```

### 3. Next-Day Predictor

```bash
# Navigate to engine
cd engines/nextday

# Generate prediction (same as Replit)
python cli.py

# Train models (same as Replit)
python cli.py --train

# Check status (same as Replit)
python cli.py --status
```

### 4. SMS Testing

```bash
# Test SMS (same as Replit)
python test_sms_integration.py
```

---

## 🖥️ Cursor AI Setup

### Step 1: Open Project

1. Open Cursor AI
2. File → Open Folder
3. Select your cloned repository

### Step 2: Select Python Interpreter

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: "Python: Select Interpreter"
3. Choose: `./venv/bin/python` (Mac/Linux) or `.\venv\Scripts\python.exe` (Windows)

### Step 3: Verify Setup

Open terminal in Cursor (`` Ctrl+` ``):

```bash
# Check Python
python --version

# Check packages
pip list | grep -E "lightgbm|pandas|flask|twilio"

# Test system
python main.py --mode test
```

### Step 4: Run Predictions

```bash
# Same commands as Replit
python main.py --mode single --symbol AMD
```

---

## 📁 Directory Structure (Auto-Created)

The setup script creates these automatically:

```
├── venv/                    # Virtual environment (created by setup)
├── .env                     # Your secret keys (you create from .env.example)
├── data/
│   ├── cache/              # Created by setup
│   ├── predictions/        # Created by setup
│   ├── nextday/           # Created by setup
│   └── weekend/           # Created by setup
├── logs/                   # Created by setup
│   ├── predictions.csv    # Auto-generated when running
│   ├── errors.log         # Auto-generated when running
│   └── performance.log    # Auto-generated when running
└── models/                # Created by setup
```

---

## ✅ Complete Setup Checklist

### On Replit (Before Exporting)

- [ ] Run: `env | grep -E "POLYGON|ALPHA|EODHD|FINNHUB|TWILIO|REDDIT|FRED|DATABASE" > my_keys_backup.txt`
- [ ] Download or copy the keys
- [ ] Push code to Git: `git push origin main`

### On Local Machine

- [ ] Clone repository: `git clone <repo-url>`
- [ ] Run setup: `./setup.sh` (Mac/Linux) or `setup.bat` (Windows)
- [ ] Create `.env`: `cp .env.example .env`
- [ ] Paste all keys from Replit into `.env`
- [ ] Test: `python main.py --mode test`
- [ ] Run: `python main.py --mode single --symbol AMD`

### In Cursor AI

- [ ] Open folder in Cursor
- [ ] Select Python interpreter (venv)
- [ ] Verify terminal uses venv: `which python` should show `venv/bin/python`
- [ ] Test: `python main.py --mode test`

---

## 🔄 Database Options

You have `DATABASE_URL` in Replit. Choose one:

### Option 1: Use Replit Database Remotely

```bash
# Just copy DATABASE_URL to local .env
DATABASE_URL=<same_url_from_replit>
```

### Option 2: Local PostgreSQL

```bash
# Install PostgreSQL
brew install postgresql          # Mac
sudo apt install postgresql      # Linux

# Start it
brew services start postgresql   # Mac
sudo service postgresql start    # Linux

# Create database
createdb stock_predictions_local

# Update .env
DATABASE_URL=postgresql://localhost:5432/stock_predictions_local
```

---

## 🐛 Troubleshooting

### Issue: Packages Not Found

**Solution:**
```bash
# Verify venv is activated (you should see (venv) in terminal)
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall
pip install -r requirements.txt
```

### Issue: API Keys Not Loading

**Solution:**
```bash
# Check .env exists
ls -la .env

# Install dotenv if missing
pip install python-dotenv

# Test loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ALPHA_VANTAGE_API_KEY'))"
```

### Issue: Import Errors in Cursor

**Solution:**
1. Reload window: `Cmd+Shift+P` → "Reload Window"
2. Reselect interpreter: `Cmd+Shift+P` → "Python: Select Interpreter" → choose venv
3. Restart terminal: Close and open new terminal (`` Ctrl+` ``)

---

## 🎯 Final Verification

Run these commands to verify everything works:

```bash
# 1. Activate venv
source venv/bin/activate  # or venv\Scripts\activate

# 2. Check Python
python --version  # Should be 3.8+

# 3. Check packages
pip list | wc -l  # Should show 50+ packages

# 4. Check keys
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Keys OK' if os.getenv('POLYGON_API_KEY') else 'Keys MISSING')"

# 5. Test system
python main.py --mode test

# 6. Run prediction
python main.py --mode single --symbol AMD
```

If all pass ✅, you're ready to use in Cursor AI!

---

## 📚 Documentation Files

- **README.md** - Complete system documentation
- **SETUP_GUIDE.md** - Quick setup guide
- **CURSOR_AI_GUIDE.md** - Cursor AI specific guide
- **YOUR_SECRET_KEYS.md** - Your specific keys to transfer
- **api_key_requirements.md** - API providers info
- **requirements.txt** - All Python packages
- **.env.example** - Environment template
- **setup.sh / setup.bat** - Automated setup scripts

---

## 🚀 You're All Set!

The system will run EXACTLY the same as on Replit, just on your local machine with Cursor AI!

**Commands are identical:**
- `python main.py --mode run --symbol AMD --interval 10`
- `cd engines/after_close_engine && python serve.py`
- `cd engines/nextday && python cli.py --train`

**Use Cursor AI features:**
- `Cmd+L` - Ask AI about code
- `Cmd+K` - Edit code with AI
- AI understands the full codebase from README.md

Happy trading! 🎉📈
