# Analysis: Why System Predicted UP When Stocks Went DOWN

Date: October 16, 2024
Prediction: Both AMD and AVGO UP
Reality: Both went DOWN
Issue: System missed bearish signals

## ROOT CAUSES:

### 1. NEWS IS 2 DAYS OLD
- Code fetches news from last 48 hours
- Market sentiment shifts quickly
- Old bullish news counted as current bullish signal
- Weight: 13-16% (very high)
- Impact: Strong false positive

FIX: Use only last 6-12 hours of news, not 48 hours

### 2. KEYWORD MATCHING TOO SIMPLE
- Just counts words like surge, rally, drop, fall
- No context or nuance
- Misses sarcasm or hedging
- Could count old earnings beat as bullish even if stock sold off

FIX: Use proper NLP sentiment analysis or weight recent articles higher

### 3. FUTURES WEIGHT TOO LOW
- Futures were negative (ES -0.78%, NQ -0.58%)
- But only 13% weight
- News 13-16% outweighed futures
- Score: Only -0.009 to -0.012 impact

FIX: Increase futures weight when predicting next-day, or reduce news weight

### 4. TECHNICAL INDICATORS LAG
- RSI 77.9 (overbought!) scored as bullish +0.130
- MACD bullish but lagging
- Uptrend but could be topping
- These are backward-looking

FIX: High RSI should be bearish (reversal risk), not bullish

### 5. PRE-MARKET TOO LOW WEIGHT
- AMD pre-market: -1.80% (significant!)
- Weight: Only 6%
- Impact: Only -0.042 score
- Got drowned out by news and technical

FIX: Increase pre-market weight for same-day weakness

### 6. MISSING MARKET CONTEXT
- System does not check advance/decline ratio
- No market breadth analysis
- No sector rotation detection
- No treasury yield impact
- No dollar strength detailed analysis

FIX: Add market internals check

## SCORING BREAKDOWN:

AMD (Total: +0.233):
- News: +0.130 (STALE, 2 days old)
- Technical: +0.130 (LAGGING, RSI overbought)
- Analyst: +0.045 (OK but long-term)
- Futures: -0.012 (TOO WEAK weight)
- Pre-market: -0.042 (TOO WEAK weight)
- VIX: -0.018 (TOO WEAK weight)

Bullish: +0.305 (mostly stale/lagging)
Bearish: -0.072 (real-time signals underweighted)

Result: System saw 2-day-old bullish news and lagging technical indicators
        But missed TODAY's bearish momentum

## RECOMMENDED FIXES:

1. News timeframe: 2 days -> 12 hours
2. News weight: 13-16% -> 8-10%
3. Futures weight: 13% -> 18%
4. Pre-market weight: 6% -> 10%
5. Technical: High RSI (>70) = bearish, not bullish
6. Add market breadth factor (5% weight)
7. Add recency multiplier: newer signals weighted 2x

## CONCLUSION:

System is NOT biased toward UP
System DID see bearish signals (futures, VIX, pre-market)
Problem: STALE bullish signals (2-day news, lagging RSI) outweighed FRESH bearish signals
Fix: Weight recent/real-time signals higher than stale signals
