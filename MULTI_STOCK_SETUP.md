# 🚀 Multi-Stock Prediction System - AMD & AVGO

Your system now supports **multiple stocks** with **stock-specific configurations**!

## 📊 Currently Active Stocks

| Symbol | Name | Volatility | Min Confidence | Reddit Weight | News Weight |
|--------|------|------------|----------------|---------------|-------------|
| **AMD** | Advanced Micro Devices | 2.0% | 65% | 12% | 20% |
| **AVGO** | Broadcom Inc | 1.5% | 62% | 5% | 25% |

---

## ✅ What's New

### 1. **Stock-Specific Weight Adjustments**
Each stock has optimized factor weights based on its characteristics:

**AMD:**
- Higher Reddit weight (12%) - Popular on WallStreetBets
- Balanced weights across all factors
- Retail-driven momentum

**AVGO:**
- Higher News weight (25%) - M&A and partnership driven
- Lower Reddit weight (5%) - Less retail coverage  
- Institutional-focused

### 2. **Stock-Specific Configurations**
See `stock_config.py` for:
- Typical volatility patterns
- Sector ETF tracking
- Competitor lists
- News keywords
- Min confidence thresholds

### 3. **Contrarian Safeguard DISABLED**
The contrarian safeguard that flips predictions is now **DISABLED by default** because:
- ❌ It contradicts your 4 PM close analysis
- ❌ Causes overnight prediction flips
- ❌ You want: "Close UP → Predict UP overnight"

---

## 🎯 How to Use

### **Option 1: Run Multi-Stock Predictor**
Predict both AMD and AVGO at once:
```bash
python multi_stock_predictor.py
```

### **Option 2: Run Single Stock**
Predict just one stock:
```bash
# For AMD
python comprehensive_nextday_predictor.py

# For AVGO (pass symbol as argument or edit DEFAULT_SYMBOL)
# You'll need to modify the script to accept command-line args
```

### **Option 3: Scheduled Predictions (4 PM Daily)**
The scheduler now predicts BOTH stocks automatically:
```bash
python new_scheduled_predictor.py
```

This will:
- Run at 4:00 PM ET every weekday
- Predict AMD first, then AVGO
- Save results to `data/nextday/latest_prediction.json`
- Show summary of both predictions

---

## 📁 File Structure

```
StockSense2/
├── stock_config.py              # ⭐ NEW: Multi-stock configuration
├── comprehensive_nextday_predictor.py  # Updated with stock-specific weights
├── multi_stock_predictor.py     # ⭐ NEW: Multi-stock runner
├── new_scheduled_predictor.py   # Updated for multi-stock
├── analyze_avgo_gaps.py         # ⭐ NEW: AVGO gap analysis tool
└── data/
    ├── nextday/
    │   └── latest_prediction.json  # Latest predictions
    └── multi_stock/
        └── predictions_*.json      # Multi-stock prediction history
```

---

## ⚙️ Configuration

### Add a New Stock

Edit `stock_config.py`:

```python
STOCK_CONFIGS['NVDA'] = {
    'name': 'NVIDIA Corporation',
    'sector_etf': 'XLK',
    'competitors': ['AMD', 'INTC', 'AVGO'],
    'typical_volatility': 0.025,  # 2.5% daily
    'min_confidence_threshold': 0.65,
    'weight_adjustments': {
        'news': 0.22,
        'futures': 0.20,
        'options': 0.15,
        'technical': 0.15,
        'sector': 0.10,
        'reddit': 0.10,
        'institutional': 0.08
    },
    'news_keywords': ['AI', 'GPU', 'data center', 'Hopper', 'Blackwell'],
    'momentum_continuation_rate': 0.58,
    'description': 'AI GPU leader with high momentum'
}

# Add to active list
ACTIVE_STOCKS.append('NVDA')
```

### Disable a Stock

Edit `stock_config.py`:
```python
# Remove from active list
ACTIVE_STOCKS = ['AMD']  # Only AMD, no AVGO
```

---

## 📊 Prediction Output Examples

### AMD Prediction
```
🎯 Loaded config for AMD: Advanced Micro Devices
   Typical Volatility: 2.0%

⚖️ Using AMD-specific weights:
   Futures         0.20 (20%)
   News            0.20 (20%)
   Options         0.15 (15%)
   Technical       0.15 (15%)
   Reddit          0.12 (12%)
   Sector          0.10 (10%)
   Institutional   0.08 (8%)

📊 AMD PREDICTION FOR NEXT TRADING DAY
Direction: UP
Confidence: 72.5%
```

### AVGO Prediction
```
🎯 Loaded config for AVGO: Broadcom Inc
   Typical Volatility: 1.5%

⚖️ Using AVGO-specific weights:
   News            0.25 (25%)  ← Higher for M&A/deals
   Futures         0.20 (20%)
   Options         0.15 (15%)
   Technical       0.13 (13%)
   Sector          0.12 (12%)
   Institutional   0.10 (10%)
   Reddit          0.05 (5%)   ← Lower retail coverage

📊 AVGO PREDICTION FOR NEXT TRADING DAY
Direction: UP
Confidence: 68.2%
```

---

## 🎯 Key Insights from Gap Analysis

### AMD
- ✅ **56% momentum continuation** - Good for predictions!
- ✅ **52% significant gaps (>1%)** - Lots of opportunities
- ✅ **1.83% average gap** - Good profit potential
- ✅ **Strong retail following** - Reddit sentiment works well

### AVGO
- ⚠️ **41% momentum continuation** - More unpredictable
- ⚠️ **34% significant gaps (>1%)** - Fewer opportunities
- ✅ **1.22% average gap** - Still tradeable ($4-5 moves)
- ✅ **News-driven** - OpenAI deals, M&A create opportunities
- ⚠️ **Less social sentiment data** - Reddit weight reduced to 5%

---

## 💡 Trading Strategy

### For AMD:
- **Best for**: Momentum trading, social sentiment plays
- **Watch**: WSB sentiment, semiconductor sector
- **Higher confidence threshold**: 65% (more predictable)

### For AVGO:
- **Best for**: News-driven trades, institutional flow
- **Watch**: M&A rumors, AI partnership announcements, earnings
- **Lower confidence threshold**: 62% (accommodate volatility)

### For Both:
- ✅ Predict at 4 PM close
- ✅ Hold prediction overnight
- ✅ No flips or reversals
- ✅ Trade at market open (9:30 AM)

---

## 🔧 Troubleshooting

### "Stock config not found"
Make sure `stock_config.py` exists and is imported properly.

### "Prediction filtered out"
The prediction didn't meet minimum confidence. This is GOOD - it prevents bad trades.

### "Multiple API key warnings"
Some APIs are optional. The system works with whatever APIs you have configured.

---

## 📝 Next Steps

1. **Test both stocks**: Run `python multi_stock_predictor.py`
2. **Compare performance**: Track which stock your system predicts better
3. **Adjust weights**: If predictions are wrong, tweak weight_adjustments in `stock_config.py`
4. **Add more stocks**: Follow the "Add a New Stock" section above

---

## 🎉 You're All Set!

Your system now predicts both **AMD** and **AVGO** with:
- ✅ Stock-specific factor weights
- ✅ Optimized confidence thresholds
- ✅ No overnight prediction flips
- ✅ Scheduled 4 PM daily predictions

Run `python multi_stock_predictor.py` to see it in action! 🚀
