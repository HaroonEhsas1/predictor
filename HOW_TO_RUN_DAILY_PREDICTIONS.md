# 📋 HOW TO RUN DAILY PREDICTIONS

**Run this EVERY DAY at 3:50 PM before market close**

---

## 🚀 **QUICK START (ONE COMMAND!):**

### **Run Enhanced Multi-Stock Predictor:**

```bash
python multi_stock_enhanced_predictor.py
```

**This runs ALL 3 stocks (AMD, AVGO, ORCL) with ALL enhancements:**
- ✅ Stock-specific catalyst detection
- ✅ Symbol-specific Reddit/Twitter sentiment
- ✅ All bias fixes and improvements
- ✅ Complete analysis for all stocks

---

## ⏰ **DAILY WORKFLOW:**

### **3:50 PM (10 minutes before close):**

```bash
cd D:\StockSense2
python multi_stock_enhanced_predictor.py
```

**What it does:**
1. Analyzes AMD (with AMD catalysts)
2. Analyzes AVGO (with AVGO catalysts)
3. Analyzes ORCL (with ORCL catalysts)
4. Shows which to trade
5. Gives entry/exit instructions

**Takes:** 2-3 minutes to run

---

## 📊 **EXAMPLE OUTPUT:**

```
================================================================================
🚀 ENHANCED MULTI-STOCK OVERNIGHT SWING PREDICTOR
================================================================================
📅 Date: 2025-10-27 03:50 PM
🎯 Stocks: AMD, AVGO, ORCL
💡 Includes: Catalyst Detection + Reddit/Twitter Fix + All Enhancements
================================================================================

================================================================================
📊 ANALYZING AMD
================================================================================

🔍 Fetching data for AMD...
📰 Fetching news for catalyst analysis...

   📊 AMD Catalysts Detected: 2
      Sentiment: POSITIVE
      Score: +0.120
      Top Catalysts:
         📈 datacenter_ai_wins: +0.080
         📈 gaming_gpu: +0.040

   🎯 Enhancement Impact:
      Score: 0.065 → 0.185 (+0.120)
      Confidence: 68.2% → 78.5%
      Direction: UP → UP

================================================================================
✅ AMD PREDICTION COMPLETE
================================================================================

📈 Direction: UP
💪 Confidence: 78.5%
💰 Current Price: $252.42
🎯 Target Price: $260.50
🛑 Stop Loss: $248.30
🚀 Catalyst Boost: +0.120

✅ TRADEABLE (Confidence ≥ 60%)
   Position Size: 75% (Good Confidence)
   Entry: Market on close at 4:00 PM
   Exit: Market open at 9:30 AM (first minute)

================================================================================
📊 ANALYZING AVGO
================================================================================
...

================================================================================
📋 TRADING SUMMARY
================================================================================

AMD:
  📈 UP @ 78.5% confidence
  $252.42 → $260.50
  ✅ TRADE

AVGO:
  📈 UP @ 82.3% confidence
  $355.43 → $363.20
  ✅ TRADE

ORCL:
  ➡️ NEUTRAL @ 58.2% confidence
  $283.76 → $285.10
  ❌ SKIP

================================================================================
🎯 Total Tradeable Signals: 2/3
================================================================================

💡 Next Steps:
   1. Review predictions above
   2. Enter positions at 4:00 PM (market close)
   3. Exit at 9:30 AM (market open, first minute)
   4. Expect 75-85% of target at market open

================================================================================
✅ ANALYSIS COMPLETE
================================================================================
```

---

## 💡 **WHAT THE OUTPUT MEANS:**

### **Direction:**
- 📈 UP = Buy (expect price increase)
- 📉 DOWN = Short or avoid (expect price decrease)
- ➡️ NEUTRAL = No clear signal (skip)

### **Confidence:**
- 85%+ = Very strong signal (100% position size)
- 75-84% = Strong signal (75% position size)
- 60-74% = Moderate signal (50% position size)
- <60% = Filtered out (skip trade)

### **Catalyst Boost:**
- Shows how much catalyst detection improved the signal
- Positive = Bullish catalysts found
- Negative = Bearish catalysts found

---

## 🎯 **DECISION MAKING:**

### **✅ TRADE IF:**
- Confidence ≥ 60%
- Direction is UP or DOWN (not NEUTRAL)
- You agree with the analysis

### **❌ SKIP IF:**
- Confidence < 60%
- Direction is NEUTRAL
- Conflicting signals noted

---

## 📱 **AFTER RUNNING:**

### **4:00 PM - Enter Trades:**
- Place market orders for selected stocks
- Enter at close price
- Set alerts for 9:30 AM

### **9:30 AM Next Day - Exit Trades:**
- Exit in first minute (9:30-9:31 AM)
- Use market orders for quick exit
- Lock in profits!

---

## 🔧 **ALTERNATIVE COMMANDS:**

### **Run Individual Stock (with catalysts):**

```bash
# AMD only
python multi_stock_enhanced_predictor.py  # Then select AMD

# AVGO only
python multi_stock_enhanced_predictor.py  # Then select AVGO

# ORCL only (original enhanced version)
python orcl_enhanced_predictor.py
```

### **Run Without Catalysts (basic):**

```bash
python multi_stock_predictor.py
```

---

## ⚙️ **TROUBLESHOOTING:**

### **Error: "Module not found"**
```bash
# Make sure you're in the right directory
cd D:\StockSense2

# Check Python environment
python --version
```

### **Error: "API key not found"**
```bash
# Check .env file exists
# Verify API keys are set
```

### **Takes too long (>5 minutes)**
```bash
# This is normal first run
# Subsequent runs are faster (cached data)
```

---

## 📊 **WHAT GETS ANALYZED:**

**For Each Stock (AMD, AVGO, ORCL):**
1. ✅ Futures sentiment (ES/NQ)
2. ✅ Options flow (P/C ratio, unusual activity)
3. ✅ Premarket prices
4. ✅ News sentiment (stock-specific articles)
5. ✅ Reddit sentiment (stock-specific mentions)
6. ✅ Twitter sentiment (stock-specific tweets)
7. ✅ Technical indicators (RSI, MACD, moving averages)
8. ✅ Analyst ratings
9. ✅ Institutional flow
10. ✅ **Catalyst detection (NEW!)**
    - AMD: Gaming, AI, data center catalysts
    - AVGO: M&A, VMware, iPhone catalysts
    - ORCL: Cloud, database, enterprise catalysts

**Plus Universal Indicators:**
- VIX (market fear)
- DXY (dollar strength)
- Market regime (SPY/QQQ trend)
- Hidden edge signals (Bitcoin, Gold, etc.)

---

## 🎯 **BEST PRACTICES:**

### **Timing:**
- Run at **3:50 PM** (10 min before close)
- Gives you time to review and decide
- Enter at 4:00 PM exact

### **Position Sizing:**
- Follow recommended sizes (50-100%)
- Never exceed 2% risk per trade
- Adjust for your account size

### **Exit Discipline:**
- **ALWAYS** exit at 9:30 AM (first minute)
- Don't wait for "better" price
- Lock in overnight gap immediately

### **Selective Trading:**
- Only trade 60%+ confidence
- Prefer 70%+ for better win rate
- It's OK to skip all 3 if none qualify

---

## 📋 **QUICK REFERENCE:**

```
COMMAND:
  python multi_stock_enhanced_predictor.py

WHEN:
  3:50 PM daily (before close)

WHAT IT DOES:
  Analyzes AMD, AVGO, ORCL with all enhancements

OUTPUT:
  Trade recommendations with targets

NEXT STEPS:
  Enter at 4:00 PM, exit at 9:30 AM next day
```

---

**Run this every day at 3:50 PM for overnight swing trades!** 📊⏰✅
