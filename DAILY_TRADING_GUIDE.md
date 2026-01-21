# DAILY TRADING GUIDE
## What to Run Each Morning (9:15 AM)

---

## 🎯 QUICK START (Simple)

### **Option 1: Complete Daily Analysis**
```bash
# Run at 9:15 AM
python run_premarket_predictions.py
```

**This gives you:**
- ✅ Market context (VIX, regime, correlation)
- ✅ All 4 stock analyses
- ✅ Final recommendations
- ✅ Position sizes
- ✅ Entry/exit plans

---

### **Option 2: Quick Single Stock**
```python
# In Python
from run_premarket_predictions import quick_prediction

# AMD gapped up 2.5% on 3M volume
quick_prediction('AMD', gap_pct=2.5, volume=3000000)

# NVDA gapped down 1.2% on 5M volume  
quick_prediction('NVDA', gap_pct=-1.2, volume=5000000)
```

---

### **Option 3: Custom Analysis**
```python
from stock_specific_predictors import get_predictor

# Get AMD predictor
amd = get_predictor('AMD')

# Your data
data = {
    'gap_pct': 2.5,           # 2.5% gap up
    'volume': 3000000,        # 3M premarket volume
    'min_volume': 1000000     # Stock minimum
}

# Get prediction
result = amd.predict(data)

print(f"Direction: {result['direction']}")
print(f"Confidence: {result['confidence']*100:.0f}%")
print(f"Warning: {result.get('warning', 'None')}")
```

---

## 📋 DAILY WORKFLOW

### **9:00-9:15 AM: Gather Data**
```
Check each stock:
1. Gap % from yesterday's close
2. Premarket volume
3. Any news/catalysts
4. Futures direction
```

### **9:15 AM: Run System**
```bash
python run_premarket_predictions.py
```

### **9:15-9:25 AM: Review & Decide**
```
Review:
- Market context (VIX, regime)
- Stock recommendations
- Position sizes
- Warnings (AMD 9:35 exit, etc.)

Decide:
- Which stocks to trade
- Position sizes
- Entry timing
```

### **9:25-9:30 AM: Execute**
```
If STRONG BUY/SELL:
- Enter at 9:28-9:30 AM
- Full position size

If BUY/SELL:
- Enter at 9:28-9:30 AM
- Adjusted position size

If CAUTIOUS:
- Wait for confirmation
- Half position size

If SKIP:
- Don't trade
```

### **9:30-9:35 AM: Manage AMD**
```
⚠️ AMD SPECIAL RULE:
- If traded AMD UP
- EXIT at 9:35 AM
- Capture gap, avoid reversal (45.5% risk!)

Other stocks:
- Set stops (ATR-based)
- Set targets
- Monitor
```

---

## 📊 UNDERSTANDING OUTPUT

### **Market Context:**
```
Threshold: 12 points (NORMAL)
  - How strong signal needs to be
  - Lower in calm markets, higher in volatile

Regime: RANGE_BOUND
  - Current market condition
  - Affects strategy

Correlation: 0.38 (LOW)
  - How much stocks move together
  - Max positions allowed
```

### **Stock Recommendations:**
```
AMD:
  Direction: UP
  Confidence: 67%
  Position Size: 90%
  🟢🟢 RECOMMENDATION: BUY
  EXIT: 9:35 AM (AMD reversal risk!)

Meaning:
- Trade AMD long
- Use 90% of normal position
- Exit at 9:35 AM specifically for AMD
```

### **Signal Strength:**
```
🟢🟢🟢 STRONG (75%+): Full confidence
🟢🟢 GOOD (65-75%): High confidence
🟡 CAUTIOUS (55-65%): Moderate confidence
⚪ SKIP (<55%): Too weak
```

---

## 🎯 EXAMPLES

### **Example 1: Normal Bull Day**
```
Market Context:
- VIX: 16 (Calm)
- Regime: TRENDING_BULL
- Correlation: 0.45 (Low)

Predictions:
AMD:  UP 72% → STRONG BUY (100% position)
NVDA: UP 68% → BUY (90% position)
META: UP 62% → BUY (90% position)
AVGO: NEUTRAL → SKIP

Action:
- Trade 3 stocks (AMD, NVDA, META)
- Full positions (90-100%)
- EXIT AMD at 9:35 AM
```

### **Example 2: Volatile Market**
```
Market Context:
- VIX: 32 (High)
- Regime: HIGH_VOLATILITY
- Correlation: 0.85 (Very High)

Predictions:
AMD:  UP 58% → CAUTIOUS (25% position)
NVDA: NEUTRAL → SKIP
META: NEUTRAL → SKIP
AVGO: NEUTRAL → SKIP

Action:
- Trade only 1 stock (AMD)
- Small position (25%)
- Very selective due to volatility
```

### **Example 3: Mixed Signals**
```
Market Context:
- VIX: 18 (Normal)
- Regime: RANGE_BOUND
- Correlation: 0.40 (Low)

Predictions:
AMD:  UP 65% → BUY (75% position)
NVDA: DOWN 62% → SELL SHORT (75% position)
META: NEUTRAL → SKIP
AVGO: NEUTRAL → SKIP

Action:
- Trade 2 stocks (AMD long, NVDA short)
- Diversified directions
- Range-bound adjustments applied
```

---

## ⚠️ SPECIAL RULES TO REMEMBER

### **AMD-Specific:**
```
✓ EXIT at 9:35 AM if traded UP
✓ 45.5% intraday reversal rate
✓ Capture gap, avoid reversal
✓ Most important rule!
```

### **AVGO-Specific:**
```
✓ Requires institutional confirmation
✓ 57% trap rate (highest!)
✓ Be VERY skeptical
✓ Skip if uncertain
```

### **META-Specific:**
```
✓ Needs gap >1.5% or catalyst
✓ 41% momentum (weakest)
✓ Don't chase small moves
✓ Regulatory news = fake-out
```

### **NVDA-Specific:**
```
✓ AI news = major catalyst
✓ 53% trap rate (be careful)
✓ Needs strong confirmation
✓ Follow sector closely
```

---

## 🚀 FILES TO USE

### **Main Files:**
```
run_premarket_predictions.py  ← RUN THIS DAILY
stock_specific_predictors.py  ← Individual predictors
adaptive_thresholds.py         ← VIX-based thresholds
regime_detector.py             ← Market regime
correlation_manager.py         ← Position limits
volume_profile.py              ← VWAP analysis
```

### **Test Files:**
```
test_intelligent_system.py     ← Verify intelligence
verify_enhanced_bidirectional.py ← Check no bias
comprehensive_test_suite.py    ← Full testing
```

### **Documentation:**
```
INTELLIGENT_SYSTEM_EDGE.md     ← What makes it smart
DAILY_TRADING_GUIDE.md         ← This file
PREMARKET_SYSTEM_COMPLETE.md   ← Complete docs
```

---

## 💡 TIPS

### **Best Practices:**
```
✓ Run at 9:15 AM (consistent timing)
✓ Review ALL warnings
✓ Respect position size limits
✓ EXIT AMD at 9:35 if traded
✓ Use stops always
✓ Track your results
```

### **Red Flags to Skip:**
```
❌ High VIX (>30) with weak signals
❌ AVGO without institutional confirmation
❌ META small gap (<1.5%) without catalyst
❌ All stocks correlated >0.8 (limit exposure)
❌ Your confidence doesn't match system's
```

### **When to Be Aggressive:**
```
✓ VIX <15 (calm market)
✓ Clear regime (TRENDING_BULL)
✓ Low correlation (<0.6)
✓ Stock-specific catalyst present
✓ Confidence >75%
```

### **When to Be Defensive:**
```
✓ VIX >25 (volatile)
✓ Unclear regime (TRANSITIONING)
✓ High correlation (>0.7)
✓ No catalysts
✓ Confidence 55-65%
```

---

## 📞 QUICK REFERENCE

### **Command to Run:**
```bash
python run_premarket_predictions.py
```

### **Best Time:**
```
9:15 AM EST (after premarket data available)
```

### **What You Get:**
```
1. Market context (VIX, regime, correlation)
2. Individual stock analysis (4 stocks)
3. Final recommendations with position sizes
4. Entry/exit plans
5. Risk management guidance
```

### **Decision Flow:**
```
1. Run system → 2. Review output → 3. Check warnings
         ↓
4. Decide position sizes → 5. Enter 9:25-9:30 AM
         ↓
6. Set stops/targets → 7. Manage (AMD exit 9:35)
```

---

## **YOU'RE READY TO TRADE!** 🚀

**Run at 9:15 AM tomorrow and follow the system!**

Good luck! 💰
