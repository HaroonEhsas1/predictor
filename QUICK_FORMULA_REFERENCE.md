# ⚡ Quick Formula Reference Card
**For rapid lookup during trading**

---

## 📰 NEWS SENTIMENT

```
Formula: (Bullish Articles - Bearish Articles) / Total Articles

Example:
  13 bullish, 2 bearish, 10 neutral
  = (13-2)/(13+2) = 11/15 = 0.733
  
Note: Neutral articles EXCLUDED from calculation!
```

---

## 🎯 CONFIDENCE

```python
# For UP or DOWN direction:

if |score| <= 0.10:
    confidence = 55 + (|score| * 125)
else:
    confidence = 67.5 + ((|score| - 0.10) * 115)

# Capped at 88%
```

### Quick Lookup Table:
| Score | Confidence |
|-------|-----------|
| 0.04  | 60.0% |
| 0.08  | 65.0% |
| 0.10  | 67.5% |
| 0.15  | 73.3% |
| 0.17  | 75.7% |
| 0.20  | 79.0% |
| 0.22  | 81.4% |
| 0.25  | 84.8% |
| 0.30+ | 88.0% (capped) |

---

## 📊 DIRECTION THRESHOLD

```
Score >= +0.04 → UP
Score <= -0.04 → DOWN
Between → NEUTRAL
```

---

## 🎯 TARGET VOLATILITY

```python
dynamic_vol = base_vol * confidence_mult * vix_mult * premarket_mult
```

### Multipliers:
```
Confidence 85%+: 1.08
Confidence 75%+: 1.05
Confidence 65%+: 1.03
Confidence <65%: 1.02

VIX >25: 1.15
VIX 20-25: 1.08
VIX 15-20: 1.00
VIX <15: 0.85

Premarket gap >2%: 1.10
Premarket gap >1%: 1.05
Normal: 1.00
```

---

## ⚖️ STOCK WEIGHTS

### ORCL (Institutional):
```
Futures 16%, Institutional 16%, News 14%
Options 11%, Premarket 10%, Hidden 10%
VIX 8%, Technical 6%, Others 15%
```

### AVGO (M&A):
```
Futures 15%, News 11%, Options 11%
Premarket 10%, Institutional 10%, Hidden 10%
VIX 8%, Sector 8%, Others 17%
```

### AMD (Retail):
```
Futures 15%, Options 11%, Premarket 10%
News 8%, Technical 8%, Intraday 8%
Reddit 8%, VIX 8%, Others 24%
```

---

## 🔢 QUICK CALCULATIONS

### News Score:
```
Total = Bullish + Bearish (exclude neutrals!)
Score = (B - Bear) / Total
```

### Confidence (most common range):
```
Score 0.04: 55 + (0.04*125) = 60%
Score 0.08: 55 + (0.08*125) = 65%
Score 0.10: 55 + (0.10*125) = 67.5%

Score 0.15: 67.5 + (0.05*115) = 73.3%
Score 0.20: 67.5 + (0.10*115) = 79.0%
```

### Target Price:
```
UP: Current * (1 + dynamic_vol)
DOWN: Current * (1 - dynamic_vol)
```

---

## 🚨 KEY REMINDERS

1. **News:** Neutral articles DON'T count
2. **Confidence:** Capped at 88% (realistic)
3. **Threshold:** ±0.04 (not ±0.05)
4. **Weights:** Stock-specific (ORCL ≠ AVGO ≠ AMD)

---

## 📱 CHEAT SHEET

```
Quick Check:
  Score >+0.04 && Conf >60% = Consider BUY
  Score <-0.04 && Conf >60% = Consider SELL
  Score between ±0.04 = SKIP (neutral)
  
  Confidence >70% = Strong signal
  Confidence 60-70% = Moderate signal
  Confidence <60% = Weak signal (skip)
```
