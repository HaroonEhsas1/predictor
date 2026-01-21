"""
AVGO OVERNIGHT CHALLENGE
Predict tomorrow's close direction based on today's data
Using ACTUAL system logic
"""

print("="*80)
print("🎯 AVGO OVERNIGHT PREDICTION CHALLENGE")
print("="*80)

# ========== SCENARIO INPUTS ==========
print("\n📊 SCENARIO DATA:")
print("="*80)

stock_data = {
    'symbol': 'AVGO',
    'close': 376.47,
    'intraday_low': 372.00,
    'intraday_high': 379.50,  # Estimated
    '5day_gain': 3.2,
    'volume_trend': 'declining',
}

market_data = {
    'nasdaq_futures': -0.3,
    'sox_index': 0.0,  # Flat
    'vix': 18.5,  # Ticked higher
    'dxy': 1.2,  # Up (bearish for stocks)
    'yields': 0.8,  # Up (bearish for growth stocks)
}

options_data = {
    'heavy_calls': 390,  # $13 above current
    'put_protection': 360,  # $16 below current
    'call_put_ratio': 0.85,  # More calls than puts = bullish
}

news_sentiment = {
    'ai_chip_demand': 'slightly_slowing',  # -0.04
    'apple_supplier': 'neutral',  # 0.00
    'overall': -0.02,  # Slight negative
}

print(f"Stock: {stock_data['symbol']}")
print(f"  Today's Close: ${stock_data['close']:.2f}")
print(f"  Intraday Range: ${stock_data['intraday_low']:.2f} - ${stock_data['intraday_high']:.2f}")
print(f"  5-Day Gain: +{stock_data['5day_gain']:.1f}%")
print(f"  Volume Trend: {stock_data['volume_trend']}")

print(f"\nMarket Environment:")
print(f"  NASDAQ Futures: {market_data['nasdaq_futures']:+.1f}%")
print(f"  SOX Index: {market_data['sox_index']:+.1f}%")
print(f"  VIX: {market_data['vix']:.1f} (ticked higher)")
print(f"  DXY: +{market_data['dxy']:.1f}% (bearish for stocks)")
print(f"  Yields: +{market_data['yields']:.1f}% (bearish for growth)")

print(f"\nOptions Flow:")
print(f"  Heavy Calls: ${options_data['heavy_calls']} (+{((options_data['heavy_calls']/stock_data['close'])-1)*100:.1f}% OTM)")
print(f"  Put Protection: ${options_data['put_protection']} ({((options_data['put_protection']/stock_data['close'])-1)*100:.1f}% OTM)")
print(f"  P/C Ratio: {options_data['call_put_ratio']:.2f} (bullish)")

print(f"\nNews Sentiment:")
print(f"  AI Chip Demand: {news_sentiment['ai_chip_demand']} (concern)")
print(f"  Apple Supplier: {news_sentiment['apple_supplier']}")
print(f"  Overall News: {news_sentiment['overall']:+.2f}")

# ========== SYSTEM ANALYSIS ==========
print(f"\n{'='*80}")
print("🤖 SYSTEM ANALYSIS:")
print("="*80)

# 1. TECHNICAL ANALYSIS
daily_range = stock_data['intraday_high'] - stock_data['intraday_low']
close_from_low = stock_data['close'] - stock_data['intraday_low']
close_position = (close_from_low / daily_range) * 100

print(f"\n1️⃣ TECHNICAL SIGNALS:")
print(f"  Close Position: {close_position:.0f}% of range")
if close_position > 60:
    technical_signal = +0.05
    print(f"  → Closed near highs: BULLISH (+0.05)")
elif close_position < 40:
    technical_signal = -0.05
    print(f"  → Closed near lows: BEARISH (-0.05)")
else:
    technical_signal = 0.00
    print(f"  → Closed mid-range: NEUTRAL")

# RSI estimate (after 5-day +3.2% gain)
estimated_rsi = 58  # Likely neutral-to-bullish
print(f"  Estimated RSI: {estimated_rsi} (neutral)")

# Momentum
momentum_score = stock_data['5day_gain'] / 100 * 0.56  # 56% continuation rate
print(f"  5-Day Momentum: +{stock_data['5day_gain']:.1f}% → Score: +{momentum_score:.3f}")

# Volume declining = distribution warning
if stock_data['volume_trend'] == 'declining':
    volume_penalty = -0.03
    print(f"  Volume Declining: WARNING (distribution) → {volume_penalty:.3f}")
else:
    volume_penalty = 0
    print(f"  Volume: Normal")

technical_score = technical_signal + momentum_score + volume_penalty
print(f"  TECHNICAL TOTAL: {technical_score:+.3f}")

# 2. OPTIONS ANALYSIS
print(f"\n2️⃣ OPTIONS SIGNALS:")
pcr = options_data['call_put_ratio']
if pcr < 0.9:
    options_score = +0.08  # Bullish (more calls)
    print(f"  P/C Ratio {pcr:.2f} < 0.9: BULLISH (call heavy)")
elif pcr > 1.2:
    options_score = -0.06  # Bearish (more puts)
    print(f"  P/C Ratio {pcr:.2f} > 1.2: BEARISH (put heavy)")
else:
    options_score = 0.02
    print(f"  P/C Ratio {pcr:.2f}: NEUTRAL-BULLISH")

# Heavy OTM calls = bullish bias
call_distance = ((options_data['heavy_calls'] / stock_data['close']) - 1) * 100
if call_distance > 2.0:
    print(f"  Heavy Calls at ${options_data['heavy_calls']} (+{call_distance:.1f}% OTM): Target identified")
    options_score += 0.03

print(f"  OPTIONS TOTAL: {options_score:+.3f}")

# 3. NEWS/FUNDAMENTAL
print(f"\n3️⃣ NEWS/FUNDAMENTAL:")
news_score = news_sentiment['overall'] * 10  # Scale to system range
print(f"  Overall Sentiment: {news_sentiment['overall']:+.2f} → Score: {news_score:+.3f}")
print(f"  Concern: AI chip demand slowing (factored into sentiment)")
print(f"  NEWS TOTAL: {news_score:+.3f}")

# 4. SECTOR
print(f"\n4️⃣ SECTOR (SOX):")
sector_score = market_data['sox_index'] / 100
print(f"  SOX: {market_data['sox_index']:+.1f}% → Score: {sector_score:+.3f}")
print(f"  SECTOR TOTAL: {sector_score:+.3f}")

# 5. FUTURES
print(f"\n5️⃣ FUTURES:")
futures_score = market_data['nasdaq_futures'] / 100 * 0.5  # Weight 50% of move
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% → Score: {futures_score:+.3f}")
print(f"  FUTURES TOTAL: {futures_score:+.3f}")

# 6. MACRO (VIX, DXY, Yields)
print(f"\n6️⃣ MACRO HEADWINDS:")
vix_penalty = 0
if market_data['vix'] > 18:
    vix_penalty = -0.02
    print(f"  VIX {market_data['vix']:.1f} > 18: Risk-off → {vix_penalty:.3f}")

dxy_penalty = -market_data['dxy'] / 100 * 0.5  # DXY up = stocks down
print(f"  DXY: +{market_data['dxy']:.1f}% → Score: {dxy_penalty:.3f}")

yields_penalty = -market_data['yields'] / 100 * 0.3  # Yields up = growth stocks down
print(f"  Yields: +{market_data['yields']:.1f}% → Score: {yields_penalty:.3f}")

macro_score = vix_penalty + dxy_penalty + yields_penalty
print(f"  MACRO TOTAL: {macro_score:+.3f}")

# 7. APPLY WEIGHTS (AVGO-specific from stock_config)
print(f"\n{'='*80}")
print("⚖️ APPLYING AVGO-SPECIFIC WEIGHTS:")
print("="*80)

weights = {
    'technical': 0.10,
    'institutional': 0.14,  # (not available, assume neutral = 0)
    'news': 0.11,
    'futures': 0.11,
    'options': 0.11,
    'sector': 0.08,
    'vix': 0.06,
}

weighted_scores = {
    'technical': technical_score * weights['technical'],
    'options': options_score * weights['options'],
    'news': news_score * weights['news'],
    'sector': sector_score * weights['sector'],
    'futures': futures_score * weights['futures'],
    'vix': vix_penalty * weights['vix'],
    'macro': (dxy_penalty + yields_penalty) * 0.05,
}

for factor, score in weighted_scores.items():
    print(f"  {factor.capitalize():15s} {score:+.4f}")

total_score = sum(weighted_scores.values())
print(f"  {'─'*30}")
print(f"  {'TOTAL SCORE':15s} {total_score:+.4f}")

# Market regime adjustment
market_regime = -0.015  # Slight bearish (futures red, VIX up, yields up)
total_score += market_regime
print(f"  Market Regime:  {market_regime:+.4f}")
print(f"  {'─'*30}")
print(f"  {'FINAL SCORE':15s} {total_score:+.4f}")

# ========== PREDICTION ==========
print(f"\n{'='*80}")
print("🎯 FINAL PREDICTION:")
print("="*80)

if total_score > 0.04:
    direction = "UP"
    color = "🟢"
elif total_score < -0.04:
    direction = "DOWN"
    color = "🔴"
else:
    direction = "NEUTRAL"
    color = "⚪"

confidence = 55 + abs(total_score) * 125
confidence = min(confidence, 95)

print(f"\n{color} DIRECTION: {direction}")
print(f"📊 CONFIDENCE: {confidence:.1f}%")
print(f"📈 SCORE: {total_score:+.4f}")

# Calculate target
volatility = 0.0281  # AVGO typical volatility (2.81%)
expected_move = abs(total_score) * 1.5  # Volatility multiplier
target_move_pct = expected_move * 100

if direction == "UP":
    target_price = stock_data['close'] * (1 + expected_move)
    print(f"\n💰 TARGET: ${target_price:.2f} (+{target_move_pct:.1f}%)")
    print(f"   Range: ${stock_data['close'] * 1.005:.2f} - ${stock_data['close'] * 1.015:.2f}")
elif direction == "DOWN":
    target_price = stock_data['close'] * (1 - expected_move)
    print(f"\n💰 TARGET: ${target_price:.2f} (-{target_move_pct:.1f}%)")
    print(f"   Range: ${stock_data['close'] * 0.995:.2f} - ${stock_data['close'] * 0.985:.2f}")
else:
    print(f"\n💰 TARGET: ${stock_data['close']:.2f} (±0.5%)")
    print(f"   Range: ${stock_data['close'] * 0.995:.2f} - ${stock_data['close'] * 1.005:.2f}")

# ========== REASONING ==========
print(f"\n{'='*80}")
print("💡 DETAILED REASONING:")
print("="*80)

print(f"\n✅ BULLISH FACTORS:")
bullish = [
    f"Options flow bullish (P/C {pcr:.2f}, heavy calls at ${options_data['heavy_calls']})",
    f"5-day momentum +{stock_data['5day_gain']:.1f}% (56% continuation rate)",
    f"Close position {close_position:.0f}% of range (decent)",
]
for factor in bullish:
    print(f"  • {factor}")

print(f"\n⚠️ BEARISH FACTORS:")
bearish = [
    f"NASDAQ futures {market_data['nasdaq_futures']:+.1f}% (market headwind)",
    f"Volume declining (distribution warning)",
    f"VIX up (risk-off sentiment)",
    f"DXY +{market_data['dxy']:.1f}%, Yields +{market_data['yields']:.1f}% (macro headwinds)",
    f"AI chip demand concerns (slight negative sentiment)",
    f"SOX flat (no sector tailwind)",
]
for factor in bearish:
    print(f"  • {factor}")

print(f"\n⚖️ THE BALANCE:")
print(f"  Bullish strength: Options + Momentum")
print(f"  Bearish strength: Macro headwinds + Volume decline")
print(f"  Tiebreaker: {direction} (score {total_score:+.4f})")

print(f"\n🎲 RISK ASSESSMENT:")
if confidence < 60:
    print(f"  ⚠️ LOW CONFIDENCE ({confidence:.1f}%) - Skip trade or use small position")
elif confidence < 70:
    print(f"  ⚪ MODERATE CONFIDENCE ({confidence:.1f}%) - Partial position (50%)")
else:
    print(f"  ✅ HIGH CONFIDENCE ({confidence:.1f}%) - Standard position (75-100%)")

print(f"\n{'='*80}")
print("CONCLUSION:")
print("="*80)
print(f"""
AVGO is caught between:
✅ Bullish options positioning and recent momentum
⚠️ Macro headwinds and declining volume

The system predicts: {direction} with {confidence:.1f}% confidence

Key levels to watch:
  Support: ${options_data['put_protection']} (heavy put protection)
  Resistance: ${options_data['heavy_calls']} (heavy call betting)
  
Tomorrow's close likely in range: {
    f"${stock_data['close'] * 0.985:.2f} - ${stock_data['close'] * 1.015:.2f}"
}

{f"If {direction}, target ${target_price:.2f}" if direction != "NEUTRAL" else "Expect choppy, range-bound action"}
""")

print("="*80)
