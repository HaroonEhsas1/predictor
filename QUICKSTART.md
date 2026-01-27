# Quick Start Guide - Premarket Multi-Stock Predictor

## 🚀 Get Started in 30 Seconds

### 1. Run the System
```bash
cd /workspaces/predictor
python premarket_multi_stock.py
```

### 2. Read the Output
The system will show:
- Market context (VIX, SPY, NASDAQ)
- Premarket gaps for all 6 stocks
- Real-time news sentiment for each stock
- Trading recommendations with position sizes

### 3. Make Trading Decisions
- Green (🟢): STRONG_TRADE or TRADE → Take positions
- Yellow (🟡): CAUTIOUS → Consider if high conviction
- White (⚪): SKIP → Wait for better setup

---

## 📰 NEW: News Sentiment Integration

Each stock now shows:
```
AMD:
   Direction: DOWN
   Confidence: 93.8%
   News Sentiment: +0.15 (3 articles)  ← NEW!
   ...
```

**What it means:**
- Positive sentiment (+0.15): Markets expect stock to rise
- Negative sentiment (-0.15): Markets expect stock to fall
- Neutral (0.0): No clear directional bias

**How it works:**
- Fetches latest news from multiple sources
- Analyzes with AI models trained on price reactions
- Boosts confidence if sentiment aligns with gap direction

---

## 📊 Trading Recommendations

### Confidence Levels
- **70%+**: STRONG_TRADE (100% position)
- **60-70%**: TRADE (75% position)
- **50-60%**: CAUTIOUS (50% position)
- **<50%**: SKIP (don't trade)

### Example Trade Plan
```
AMD:
   Entry: $253.73
   Target: $249.92 (-1.5%)
   Stop: $256.27 (+1.0%)
   R:R Ratio: 1.5:1
```

---

## ⚠️ Important Notes

### Best Time to Run
- **9:15 AM ET** (US premarket opens)
- Data will be most fresh
- ML models most accurate during Asian/European market close

### For Best Results
1. Run between 4:00-9:30 AM ET (premarket hours)
2. Review all 6 stocks together (check correlations)
3. Look for alignment with overall market direction
4. Check news sentiment before entering

### Stocks Covered
- AMD (Semicondutors)
- NVDA (AI/GPUs)
- META (Social Media/AI)
- AVGO (Semiconductors)
- SNOW (Cloud/SaaS)
- PLTR (Government/AI)

---

## 🔍 Validation

To verify the system is working correctly:

```bash
# Comprehensive validation
python validate_complete_system.py

# Should show:
# ✅ All 6 news models loaded
# ✅ All 6 predictors working
# ✅ News integration functional
# ✅ System production ready
```

---

## 📁 Key Files

- `premarket_multi_stock.py` - Main system
- `stock_specific_predictors.py` - Individual stock logic
- `NEWS_SENTIMENT_INTEGRATION.md` - Full technical details
- `models/news_model_*.joblib` - ML sentiment models

---

## 🎯 Next Steps

1. ✅ Run `python premarket_multi_stock.py`
2. ✅ Review trading recommendations
3. ✅ Check news sentiment alignment
4. ✅ Enter positions with recommended position sizes
5. ✅ Use suggested entry/target/stop levels

---

## 💡 Tips

- All 6 stocks agreeing? = Market trend, not individual signals
- News sentiment conflicts with gap? = Be cautious on that trade
- High confidence + aligned news? = Strongest setup
- Earnings within 5 days? = Lower confidence due to uncertainty

---

## Support

For issues or questions:
- Check `NEWS_SENTIMENT_INTEGRATION.md` for API setup
- Check `PREMARKET_IMPLEMENTATION_COMPLETE.md` for architecture
- Check `validate_complete_system.py` for debugging

---

**Status**: 🟢 Ready to trade!

Last Updated: January 27, 2026
