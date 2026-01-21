# 🚀 StockSense Quick Start Guide

## ✅ System Status: READY & BALANCED

All systems are **connected, integrated, and bias-free**!

---

## 🎯 What Was Fixed

### Critical Bias Bug - FIXED ✅
- **Problem**: Technical neutral trends were scored as negative (bearish bias)
- **Fix Applied**: Neutral trends now score 0 (completely balanced)
- **Verification**: Run `python verify_no_bias.py` ✅ PASSED

---

## 🚀 Three Ways to Use the System

### 1️⃣ **Start the 4 PM Daily Scheduler** (Recommended)
```bash
# Double-click this file:
run_scheduler.bat

# Or run manually:
python new_scheduled_predictor.py
```
**What it does:**
- Monitors for 4:00 PM ET on weekdays
- Automatically predicts AMD & AVGO at market close
- Runs once per day
- Keeps running until you stop it (Ctrl+C)

---

### 2️⃣ **Run Manual Prediction Now** (Testing)
```bash
# Double-click this file:
run_manual_prediction.bat

# Or run manually:
python multi_stock_enhanced_predictor.py
```

**Includes:**
- ✅ AMD, AVGO, ORCL predictions
- ✅ Catalyst detection for each stock
- ✅ Symbol-specific Reddit/Twitter
- ✅ All improvements integrated

**What it does:**
- Predicts AMD, AVGO, and ORCL immediately
- Doesn't wait for 4 PM
- Shows full prediction details
- Saves to `data/multi_stock/`

---

### 3️⃣ **Verify No Bias** (Optional Check)
```bash
# Double-click this file:
run_bias_check.bat

# Or run manually:
python verify_no_bias.py
```
**What it does:**
- Verifies all 14 factors are balanced
- Checks for any directional bias
- Confirms UP and DOWN treated equally

---

## 📊 System Configuration

### Active Stocks:
| Stock | Volatility | Min Confidence | Key Drivers |
|-------|-----------|---------------|-------------|
| **AMD** | 2.0% | 65% | Reddit (7%), News (13%) |
| **AVGO** | 1.5% | 62% | News (16%), Institutional (7%) |

### Prediction Sources (14 Total):
✅ News Sentiment  
✅ Futures (ES/NQ)  
✅ Options Flow  
✅ Technical Analysis (BALANCED - no bias)  
✅ Sector Performance  
✅ Reddit Sentiment  
✅ Twitter Sentiment  
✅ VIX Fear Gauge  
✅ Pre-Market Action  
✅ Analyst Ratings  
✅ DXY (Dollar Index)  
✅ Earnings Proximity  
✅ Short Interest  
✅ Institutional Flow  

### Key Features:
- ✅ Stock-specific weights
- ✅ Dynamic target calculation
- ✅ Contrarian safeguard DISABLED
- ✅ No directional bias
- ✅ Completely balanced scoring

---

## 📁 Output Files

### Latest Prediction:
`data/nextday/latest_prediction.json`

### Multi-Stock Predictions:
`data/multi_stock/predictions_YYYYMMDD_HHMM.json`

### Scheduler Log:
`data/last_prediction_date.txt`

---

## 🔧 Important Settings

### Scheduler Timing:
- **Trigger**: 4:00-5:00 PM Eastern Time
- **Days**: Monday through Friday
- **Check**: Every 5 minutes
- **Stocks**: AMD, AVGO (both at once)

### Confidence Thresholds:
- **AMD**: 65% minimum
- **AVGO**: 62% minimum
- Below threshold → **HOLD** recommendation

### Direction Logic (Balanced):
- **UP**: Total score >= +0.04
- **DOWN**: Total score <= -0.04
- **NEUTRAL**: Between -0.04 and +0.04

---

## ✅ System Verification

Run this to verify everything is working:
```bash
python test_prediction_system.py
```

**Checks:**
- ✅ All modules import correctly
- ✅ Stock configs properly loaded
- ✅ API keys configured
- ✅ Prediction engine working
- ✅ Scheduler ready

---

## 🎯 What the System Predicts

For each stock (AMD, AVGO), you'll get:
- **Direction**: UP / DOWN / NEUTRAL
- **Confidence**: 50-88% (based on signal strength)
- **Current Price**: Latest market price
- **Target Price**: Next-day expected price
- **Expected Move**: Predicted change in $  and %

---

## 📋 Files Created

1. ✅ `verify_no_bias.py` - Bias verification script
2. ✅ `test_prediction_system.py` - System integration test
3. ✅ `run_scheduler.bat` - Easy scheduler launcher
4. ✅ `run_manual_prediction.bat` - Manual prediction runner
5. ✅ `run_bias_check.bat` - Bias check launcher
6. ✅ `QUICK_START.md` - This guide

---

## 🆘 Troubleshooting

### Scheduler not running at 4 PM?
- Check it's a weekday (Mon-Fri)
- Delete `data/last_prediction_date.txt` to force re-run
- Verify system time is correct

### Low confidence predictions?
- More API keys = more data = higher confidence
- Check `.env` file has API keys configured
- Run `test_prediction_system.py` to verify

### Want to test immediately?
- Run `run_manual_prediction.bat` (doesn't wait for 4 PM)
- See results instantly

---

## 🎉 You're All Set!

The system is:
- ✅ **Fully integrated** - All components connected
- ✅ **Completely balanced** - No UP/DOWN bias
- ✅ **Production ready** - Can run 24/7
- ✅ **Multi-stock** - AMD & AVGO configured

### Recommended Next Step:
```bash
# Start the daily scheduler:
run_scheduler.bat
```

The scheduler will automatically run predictions every weekday at 4 PM ET!

---

**Questions?** Check the other .md files for detailed documentation.

**System Version**: 2.0 (Multi-Stock + Bias Fix)  
**Last Updated**: October 2024
