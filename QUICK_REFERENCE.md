# 🎯 QUICK REFERENCE - Smart News Sentiment System

## One-Minute Overview

Your intraday system now **learns how each stock reacts to news** using machine learning instead of keyword counting. Trained on 90 days of historical headlines + price moves, it auto-retrains nightly.

---

## 📋 Essential Commands

### Initial Setup (One-time)
```bash
# Train models on 90 days of historical data
python news_reaction_trainer.py

# Takes ~10 min, creates models/news_model_*.joblib files
```

### Start Auto-Retraining (Background Daemon)
```bash
# Runs every night at midnight ET automatically
python scheduled_retraining.py --daemon

# Logs to: logs/retraining.log
```

### Run Live Predictions

**Single run (default: 60% model, 40% keywords):**
```bash
python intraday_multi_stock_runner.py --allow-offhours
```

**Continuous monitoring (every 5 min during market hours):**
```bash
python intraday_multi_stock_runner.py --continuous
```

**Custom model trust level (70% ML, 30% keywords):**
```bash
python intraday_multi_stock_runner.py --model-blend 0.7 --continuous
```

**Specific stocks with custom blend:**
```bash
python intraday_multi_stock_runner.py --stocks AMD,NVDA --model-blend 0.8 --allow-offhours
```

---

## 🎛️ Model Blend Weight Guide

| Weight | Meaning | Use Case |
|--------|---------|----------|
| **0.0** | 100% keywords | New market regime, avoid ML |
| **0.3** | 30% ML, 70% keywords | Conservative, high accuracy |
| **0.5** | 50/50 split | Balanced, general purpose |
| **0.6** | 60% ML, 40% keywords | **DEFAULT** — recommended |
| **0.8** | 80% ML, 20% keywords | High confidence in patterns |
| **1.0** | 100% ML | Trust model completely |

### Per-Stock Recommendations
```bash
# AMD/NVDA: More predictable → higher blend (0.7-0.8)
python intraday_1hour_predictor.py --stocks AMD,NVDA --model-blend 0.8 --allow-offhours

# PLTR/SNOW: Unpredictable → lower blend (0.3-0.5)
python intraday_1hour_predictor.py --stocks PLTR,SNOW --model-blend 0.4 --allow-offhours

# META/AVGO: Balanced → default (0.6)
python intraday_1hour_predictor.py --stocks META,AVGO --allow-offhours
```

---

## 🔍 Check Model Quality

### See training results
```bash
# Train and see accuracy scores
python news_reaction_trainer.py --stocks AMD

# Look for: accuracy > 55%, balanced precision/recall
```

### View retraining logs
```bash
tail logs/retraining.log
# Shows: timestamp, SUCCESS/FAILED status
```

### Test predictions
```bash
# Single prediction with verbose output
python intraday_1hour_predictor.py --stocks AMD --allow-offhours

# Check: "Loaded news reaction model for AMD" message
# Check: "Model-adjusted news sentiment" in output
```

---

## 🚀 Common Workflows

### Workflow 1: First-Time Setup
```bash
# 1. Train models
python news_reaction_trainer.py --days 90

# 2. Start auto-retraining daemon
python scheduled_retraining.py --daemon &

# 3. Test predictions
python intraday_multi_stock_runner.py --allow-offhours

# 4. Run live during market hours
python intraday_multi_stock_runner.py --continuous
```

### Workflow 2: Live Trading (Conservative)
```bash
# Low model blend weight (trust keywords + momentum more)
python intraday_multi_stock_runner.py --model-blend 0.3 --continuous
```

### Workflow 3: Live Trading (Aggressive)
```bash
# High model blend weight (trust ML patterns)
python intraday_multi_stock_runner.py --model-blend 0.8 --continuous
```

### Workflow 4: Specific Stocks
```bash
# Test different stocks with different blend weights
python intraday_1hour_predictor.py --stocks AMD --model-blend 0.8 --allow-offhours
python intraday_1hour_predictor.py --stocks PLTR --model-blend 0.4 --allow-offhours
```

### Workflow 5: Deep Analysis (90+ days)
```bash
# Retrain with longer history for better patterns
python news_reaction_trainer.py --days 180

# Run predictions with high confidence
python intraday_multi_stock_runner.py --model-blend 0.85 --continuous
```

---

## 📂 File Structure

```
/workspaces/predictor/
├── models/
│   ├── news_model_AMD.joblib        ← Trained model (retrains nightly)
│   ├── news_model_NVDA.joblib
│   ├── news_model_META.joblib
│   ├── news_model_AVGO.joblib
│   ├── news_model_SNOW.joblib
│   └── news_model_PLTR.joblib
│
├── logs/
│   └── retraining.log               ← Daily retraining results
│
├── data/intraday/
│   └── predictions_*.json           ← Live prediction results
│
├── news_reaction_trainer.py         ← Train models from history
├── scheduled_retraining.py          ← Auto-retrain daemon
├── intraday_1hour_predictor.py      ← Core predictor (loads models)
├── intraday_multi_stock_runner.py   ← Multi-stock orchestrator
│
├── SMART_NEWS_SENTIMENT_GUIDE.md    ← Full technical guide
└── IMPROVEMENTS_COMPLETE.md         ← This summary

```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: nltk` | Run: `pip install nltk` |
| Models not loading | Check: `ls models/` — should have 6 `.joblib` files |
| Low accuracy (~45%) | Run: `python news_reaction_trainer.py --days 180` |
| Daemon not running | Run: `python scheduled_retraining.py --daemon` in separate terminal |
| Market hours blocking | Use: `--allow-offhours` flag to run off-hours |
| Blend weight ignored | Check: You're using `--model-blend 0.X` (not `--blend`) |

---

## 📊 Example Output Interpretation

```
Loaded news reaction model for AMD (blend weight: 60%)
🎯 Direction: UP
🎯 Confidence: 85.0%
💡 Recommendation: STRONG_TRADE
📍 Position Size: 100%

📰 News Sentiment: +0.00
Articles: 0
```

**Reading This:**
- ✅ Model loaded successfully (model will be used)
- ✅ Direction: UP (momentum indicators favor up)
- ✅ Confidence: 85% (high — strong signal)
- ✅ Recommendation: STRONG_TRADE (enter full position)
- ℹ️ News: 0 articles (model not invoked for this hour)

---

## 🎓 Understanding "Model-Adjusted News Sentiment"

When you see this line:
```
🔄 Model-adjusted news sentiment: +0.50 (weight: 60%)
```

It means:
1. **Raw keyword sentiment:** -0.20 (headline keywords suggest bearish)
2. **Model prediction:** +0.80 (but ML learned similar headlines usually precede UP moves)
3. **Blended result:** -0.20 × 0.4 + 0.80 × 0.6 = **+0.40** (adjusted to bullish)
4. **Effect:** Confidence increased, direction may shift

---

## ✨ Key Features Summary

| Feature | What It Does | Command |
|---------|-------------|---------|
| **90-day training** | More data = better patterns | Default in trainer |
| **VADER sentiment** | Enriches features with tone analysis | Automatic |
| **Model blending** | Control ML vs keyword trust | `--model-blend 0-1.0` |
| **Auto-retraining** | Nightly updates at midnight ET | `--daemon` |
| **Class balancing** | Handles UP-skewed data | Automatic |
| **Metadata tracking** | Captures article source | Automatic |

---

## 🚀 Ready to Go!

**Minimal setup (2 commands):**
```bash
# Train once
python news_reaction_trainer.py

# Run continuously during market hours
python intraday_multi_stock_runner.py --continuous
```

**Advanced (custom tuning):**
```bash
# Start daemon for nightly retraining
python scheduled_retraining.py --daemon &

# Run with stock-specific blend weights
python intraday_1hour_predictor.py --stocks AMD --model-blend 0.8 --allow-offhours
```

---

## 📞 Quick Help

```bash
# Show all options
python intraday_multi_stock_runner.py -h

# Train with specific parameters
python news_reaction_trainer.py --help

# Run daemon retraining
python scheduled_retraining.py --daemon
```

---

**Last Updated:** Jan 26, 2026
**Status:** ✅ All 4 improvements implemented & tested
**Models:** ✅ Ready for production use
