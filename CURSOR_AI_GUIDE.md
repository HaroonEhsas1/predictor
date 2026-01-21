# Cursor AI Setup Guide for AMD Stock Prediction System

This guide is specifically designed to help you set up and run the AMD Stock Prediction System in Cursor AI IDE.

## 🎯 What is This System?

An advanced AI-powered stock prediction system that uses:
- **Multiple ML models**: LightGBM, CatBoost, XGBoost, LSTM/GRU ensembles
- **Institutional data**: Dark pool activity, options flow, Level 2 order book
- **Real-time predictions**: 1-minute, 10-minute, daily, and overnight gap predictions
- **Smart alerts**: SMS notifications via Twilio for trade signals
- **Risk management**: Automated position sizing and confidence gating

---

## 🚀 Quick Setup in Cursor AI

### Step 1: Open Project

1. Open Cursor AI
2. File → Open Folder
3. Select your cloned repository folder

### Step 2: Automated Setup (Recommended)

**macOS/Linux:**
```bash
# Run setup script
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
# Run setup script
setup.bat
```

The script will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create data directories
- ✅ Set up .env template
- ✅ Test the installation

### Step 3: Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 3. Install packages
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Edit .env and add API keys
```

### Step 4: Configure Python Interpreter in Cursor

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: `Python: Select Interpreter`
3. Choose: `./venv/bin/python` or `.\venv\Scripts\python.exe`
4. Cursor will now use this environment for all Python operations

### Step 5: Get API Keys (Free Tier)

**Minimum Required (FREE):**

1. **Alpha Vantage** - Get instant free key
   - Visit: https://www.alphavantage.co/support/#api-key
   - Enter email → Copy API key
   - Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`

**Optional but Recommended:**

2. **Finnhub** - Free tier available
   - Visit: https://finnhub.io/register
   - Sign up → Get API key
   - Add to `.env`: `FINNHUB_API_KEY=your_key_here`

3. **Polygon.io** - Premium ($99/mo) but best data quality
   - Visit: https://polygon.io/pricing
   - Choose plan → Get API key
   - Add to `.env`: `POLYGON_API_KEY=your_key_here`

### Step 6: Test the System

Open terminal in Cursor (`` Ctrl+` ``):

```bash
# Test installation
python main.py --mode test

# Generate single prediction
python main.py --mode single --symbol AMD
```

---

## 🤖 Using Cursor AI Features

### 1. AI Chat for Understanding Code

Press `Cmd+L` (Mac) or `Ctrl+L` (Windows) to open AI chat:

**Example questions:**
- "Explain how the after_close_engine works"
- "What does the ensemble consensus threshold do?"
- "How is risk calculated in this system?"
- "Show me where API keys are used"

### 2. AI Editing

Select code → Press `Cmd+K` (Mac) or `Ctrl+K` (Windows):

**Example prompts:**
- "Add error handling for API failures"
- "Optimize this data fetching function"
- "Add logging to this prediction method"
- "Refactor this to use async/await"

### 3. AI Debugging

When you get an error:

1. Copy the error message
2. Open AI chat (`Cmd+L` or `Ctrl+L`)
3. Paste error and ask: "Why am I getting this error and how do I fix it?"

**Example:**
```
I'm getting this error:
ModuleNotFoundError: No module named 'lightgbm'

How do I fix it?
```

### 4. Terminal Commands with AI

In terminal, type what you want to do:
```bash
# Cursor AI can help you construct commands
# Just describe what you want:
"run prediction for AMD with 5 minute intervals"
```

AI will suggest: `python main.py --mode run --symbol AMD --interval 5`

---

## 📁 Project Structure Reference for AI

When asking Cursor AI about the codebase, reference these key files:

### Main Entry Points
- `main.py` - Primary prediction system
- `engines/after_close_engine/serve.py` - API server
- `engines/nextday/cli.py` - Next-day predictor CLI

### Core Engines
- `engine/predictor.py` - Main prediction logic
- `engines/after_close_engine/engine.py` - Overnight gap prediction
- `engines/nextday/predict.py` - Next-day predictions
- `professional_trader_system.py` - Institutional insights

### Configuration
- `config.py` - Global settings
- `engines/after_close_engine/config.py` - After-close config
- `engines/nextday/config.py` - Next-day config
- `.env` - API keys and secrets (DON'T COMMIT!)

### Data & Models
- `sources/feeds.py` - Multi-source data fetching
- `engine/feature_engineer.py` - Feature engineering
- `engines/nextday/models.py` - ML model implementations
- `engine/ensemble_intraday.py` - Intraday ensemble

### Utilities
- `sms_notifier.py` - Twilio SMS alerts
- `database/prediction_database.py` - Database ORM
- `ui/printout.py` - Console output formatting

---

## 🔧 Common Cursor AI Workflows

### Workflow 1: Running Predictions

**Terminal commands:**
```bash
# Activate venv (if not auto-activated)
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Single prediction
python main.py --mode single --symbol AMD

# Continuous mode (every 10 min)
python main.py --mode run --symbol AMD --interval 10
```

### Workflow 2: Training Models

```bash
# Train next-day models
cd engines/nextday
python cli.py --train

# Check training status
python cli.py --status
```

### Workflow 3: Starting API Server

```bash
# After-close engine API
cd engines/after_close_engine
python serve.py

# Test endpoints
curl http://localhost:5050/after_close/prediction
curl http://localhost:5050/health
```

### Workflow 4: Debugging with AI

1. Run command and get error
2. Copy full error traceback
3. Open Cursor AI chat (`Cmd+L`)
4. Paste and ask: "Debug this error"
5. AI will analyze and suggest fixes

**Example:**
```python
# If you see:
KeyError: 'POLYGON_API_KEY'

# Ask AI:
"I'm getting KeyError: 'POLYGON_API_KEY'. The key is in my .env file. Why isn't it loading?"

# AI will suggest:
# 1. Check if python-dotenv is installed
# 2. Add load_dotenv() at top of file
# 3. Verify .env file location
```

---

## 🎨 Customizing with Cursor AI

### Add New Features

**Ask AI in chat:**
- "Add a feature to track prediction accuracy over time"
- "Create a function to send daily summary emails"
- "Implement a backtesting module for strategy validation"
- "Add support for multiple stock symbols"

### Modify Existing Code

**Select code → `Cmd+K` → Ask:**
- "Add retry logic with exponential backoff"
- "Convert this to async/await pattern"
- "Add comprehensive error handling"
- "Optimize this database query"

### Generate New Components

**In AI chat:**
- "Create a Discord bot integration for alerts"
- "Build a web dashboard using Flask and Chart.js"
- "Add support for cryptocurrency predictions"
- "Implement a paper trading simulator"

---

## 🐛 Troubleshooting in Cursor AI

### Issue: Python Interpreter Not Found

**Solution:**
1. `Cmd+Shift+P` → "Python: Select Interpreter"
2. If venv not listed, reload window: `Cmd+Shift+P` → "Reload Window"
3. Create new terminal: `` Cmd+` `` (will auto-activate venv)

### Issue: Module Import Errors

**Solution in Terminal:**
```bash
# Verify you're in venv
which python  # Should show path/to/venv/bin/python

# Reinstall requirements
pip install -r requirements.txt

# Check specific package
pip show lightgbm
```

**Or ask Cursor AI:**
"I'm getting ModuleNotFoundError even though I installed requirements. How do I fix this?"

### Issue: Environment Variables Not Loading

**Solution:**
1. Check `.env` file exists in project root
2. Install dotenv: `pip install python-dotenv`
3. Add to top of Python files:
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
   ```

**Or ask Cursor AI:**
"My .env file isn't loading. Here's my code: [paste code]"

### Issue: API Errors

**Solution:**
```bash
# Test API connectivity
python verify_live_data.py

# Check API quotas
# Alpha Vantage: 5 calls/min, 500/day
# Polygon: depends on plan
```

**Ask Cursor AI:**
"I'm getting '429 Too Many Requests' from Alpha Vantage. How do I add rate limiting?"

---

## 📊 Monitoring & Logs

### View Logs in Cursor

**File Explorer:**
- `logs/predictions.csv` - All predictions
- `logs/errors.log` - Error messages
- `logs/performance.log` - Performance metrics

**Terminal commands:**
```bash
# Watch predictions in real-time
tail -f logs/predictions.csv

# View recent errors
tail -20 logs/errors.log

# Search for specific errors
grep "ERROR" logs/errors.log
```

### Ask AI to Analyze Logs

**In AI chat:**
"Analyze my predictions.csv file and tell me the accuracy over the last 24 hours"

"Find all API errors in errors.log from today"

"Show me which predictions had consensus > 85%"

---

## 🚀 Advanced Cursor AI Tips

### 1. Multi-File Refactoring

Select multiple files in explorer → `Cmd+K`:
"Refactor all prediction engines to use a common interface"

### 2. Generate Tests

Open a file → `Cmd+K`:
"Generate comprehensive unit tests for this module"

### 3. Documentation

Select function → `Cmd+K`:
"Add detailed docstring with examples and type hints"

### 4. Code Review

`Cmd+L` in chat:
"Review the code in engines/after_close_engine/engine.py and suggest improvements"

### 5. Explain Complex Code

Highlight code → Right-click → "Cursor: Explain":
Gets instant explanation of what the code does

---

## 🔑 Essential Cursor AI Shortcuts

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| AI Chat | `Cmd+L` | `Ctrl+L` |
| AI Edit | `Cmd+K` | `Ctrl+K` |
| Command Palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| Terminal | `` Cmd+` `` | `` Ctrl+` `` |
| File Search | `Cmd+P` | `Ctrl+P` |
| Global Search | `Cmd+Shift+F` | `Ctrl+Shift+F` |

---

## 📚 Learning Resources

### Ask Cursor AI About:

1. **System Architecture**
   - "Explain the overall architecture of this stock prediction system"
   - "How do the different engines work together?"
   - "What's the data flow from API to prediction?"

2. **ML Models**
   - "What ML models are used and why?"
   - "How does ensemble voting work in this system?"
   - "Explain the feature engineering process"

3. **Trading Logic**
   - "How are position sizes calculated?"
   - "What are the gating requirements for trades?"
   - "Explain the risk management strategy"

4. **Integration**
   - "How do I add a new data source?"
   - "How can I integrate this with my broker API?"
   - "Show me how to add a new ML model to the ensemble"

---

## ✅ Final Checklist

Before running in production:

- [ ] Python 3.8+ installed and venv activated
- [ ] All packages installed: `pip list | grep -E "lightgbm|pandas|flask"`
- [ ] `.env` file configured with API keys
- [ ] At least Alpha Vantage API key set
- [ ] Test passed: `python main.py --mode test`
- [ ] Single prediction works: `python main.py --mode single --symbol AMD`
- [ ] Logs directory created and writable
- [ ] API server runs: `cd engines/after_close_engine && python serve.py`

---

## 🎉 You're Ready!

Now you can:

1. **Run predictions**: `python main.py --mode run --symbol AMD --interval 10`
2. **Use Cursor AI**: `Cmd+L` to ask questions about the codebase
3. **Customize code**: `Cmd+K` to edit with AI assistance
4. **Debug issues**: Paste errors into AI chat for help

**Pro Tip:** Save your favorite Cursor AI prompts as snippets:
- File → Preferences → User Snippets → New Snippet

Happy coding with Cursor AI! 🚀📈
