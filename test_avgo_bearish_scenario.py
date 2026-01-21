"""
AVGO BEARISH SCENARIO TEST
Predict overnight direction with clear bearish signals
"""

print("="*80)
print("🔴 AVGO BEARISH SCENARIO - OVERNIGHT PREDICTION")
print("="*80)

# ========== INPUTS ==========
print("\n📊 SCENARIO DATA:")
print("="*80)

stock_data = {
    'symbol': 'AVGO',
    'close': 372.10,
    'intraday_low': 369.50,
    'intraday_high': 373.40,
    '5day_change': -2.8,
    'volume_trend': 'rising_on_decline',  # Distribution!
    'rsi': 42,
}

market_data = {
    'nasdaq_futures': -0.8,
    'sox_index': -1.1,
    'vix': 20.3,
    'dxy': +0.9,
    'yields': +1.1,
    'global_equities': -1.0,
}

options_data = {
    'put_call_ratio': 1.35,  # Bearish
    'large_puts': '360-365',
    'call_volume': 'very_light',
}

news_sentiment = {
    'ai_chip_delays': -0.15,  # Major negative
    'analyst_downgrades': -0.08,
    'no_positive_news': -0.02,
    'overall': -0.25,  # Strongly bearish
}

print(f"Stock: {stock_data['symbol']}")
print(f"  Close: ${stock_data['close']:.2f}")
print(f"  Range: ${stock_data['intraday_low']:.2f} - ${stock_data['intraday_high']:.2f}")
print(f"  5-Day: {stock_data['5day_change']:+.1f}%")
print(f"  Volume: {stock_data['volume_trend']}")
print(f"  RSI: {stock_data['rsi']} (approaching oversold)")

print(f"\nMarket Environment:")
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}%")
print(f"  SOX: {market_data['sox_index']:+.1f}%")
print(f"  VIX: {market_data['vix']:.1f} (SPIKING)")
print(f"  DXY: {market_data['dxy']:+.1f}%")
print(f"  Yields: {market_data['yields']:+.1f}%")

print(f"\nOptions:")
print(f"  P/C Ratio: {options_data['put_call_ratio']:.2f} (BEARISH)")
print(f"  Large Puts: ${options_data['large_puts']}")
print(f"  Call Volume: {options_data['call_volume']}")

print(f"\nNews:")
print(f"  Overall Sentiment: {news_sentiment['overall']:+.2f} (VERY NEGATIVE)")

# ========== SYSTEM ANALYSIS ==========
print(f"\n{'='*80}")
print("🤖 SYSTEM ANALYSIS:")
print("="*80)

# 1. TECHNICAL
daily_range = stock_data['intraday_high'] - stock_data['intraday_low']
close_from_low = stock_data['close'] - stock_data['intraday_low']
close_position = (close_from_low / daily_range) * 100

print(f"\n1️⃣ TECHNICAL SIGNALS:")
print(f"  Close Position: {close_position:.0f}% of range")

if close_position > 60:
    close_signal = +0.04
    print(f"  → Near highs: Neutral-bullish (+0.04)")
elif close_position < 40:
    close_signal = -0.05
    print(f"  → Near lows: BEARISH (-0.05)")
else:
    close_signal = 0.00
    print(f"  → Mid-range: Neutral")

# RSI analysis
rsi = stock_data['rsi']
if rsi < 30:
    rsi_signal = +0.08  # Oversold bounce
    print(f"  RSI {rsi}: OVERSOLD (bounce setup) +0.08")
elif rsi < 45:
    rsi_signal = +0.03  # Approaching oversold (mild bullish)
    print(f"  RSI {rsi}: Approaching oversold (mild bullish) +0.03")
elif rsi > 65:
    rsi_signal = -0.08  # Overbought
    print(f"  RSI {rsi}: Overbought -0.08")
else:
    rsi_signal = 0.00
    print(f"  RSI {rsi}: Neutral 0.00")

# 5-day momentum
momentum = stock_data['5day_change'] / 100 * 0.41  # AVGO 41% continuation
print(f"  5-Day Momentum: {stock_data['5day_change']:+.1f}% → {momentum:+.3f}")

# Volume analysis
if stock_data['volume_trend'] == 'rising_on_decline':
    volume_signal = -0.08  # Distribution!
    print(f"  Volume Rising on Decline: DISTRIBUTION! {volume_signal:+.3f}")
else:
    volume_signal = 0.00

technical_score = close_signal + rsi_signal + momentum + volume_signal
print(f"  TECHNICAL TOTAL: {technical_score:+.3f}")

# 2. OPTIONS
print(f"\n2️⃣ OPTIONS SIGNALS:")
pcr = options_data['put_call_ratio']

if pcr > 1.5:
    # Excessive fear - contrarian bullish
    options_score = +0.06
    print(f"  P/C {pcr:.2f} > 1.5: EXCESSIVE FEAR (contrarian bullish) +0.06")
elif pcr > 1.2:
    # Heavy bearish positioning
    options_score = -0.08
    print(f"  P/C {pcr:.2f} > 1.2: HEAVY BEARISH POSITIONING {options_score:+.3f}")
elif pcr < 0.8:
    # Bullish
    options_score = +0.08
    print(f"  P/C {pcr:.2f} < 0.8: BULLISH +0.08")
else:
    options_score = 0.00
    print(f"  P/C {pcr:.2f}: Neutral")

print(f"  Large puts at $360-365: Confirms bearish bias")
print(f"  OPTIONS TOTAL: {options_score:+.3f}")

# 3. NEWS
print(f"\n3️⃣ NEWS/FUNDAMENTAL:")
news_score = news_sentiment['overall']
print(f"  AI Chip Delays: {news_sentiment['ai_chip_delays']:+.3f}")
print(f"  Analyst Downgrades: {news_sentiment['analyst_downgrades']:+.3f}")
print(f"  No Positive News: {news_sentiment['no_positive_news']:+.3f}")
print(f"  NEWS TOTAL: {news_score:+.3f}")

# 4. SECTOR
print(f"\n4️⃣ SECTOR (SOX):")
sector_score = market_data['sox_index'] / 100
print(f"  SOX: {market_data['sox_index']:+.1f}% → {sector_score:+.3f}")
print(f"  SECTOR TOTAL: {sector_score:+.3f}")

# 5. FUTURES
print(f"\n5️⃣ FUTURES:")
futures_score = market_data['nasdaq_futures'] / 100 * 0.5
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% → {futures_score:+.3f}")
print(f"  FUTURES TOTAL: {futures_score:+.3f}")

# 6. MACRO
print(f"\n6️⃣ MACRO ENVIRONMENT:")
vix_penalty = 0
if market_data['vix'] > 20:
    vix_penalty = -0.04  # Risk-off
    print(f"  VIX {market_data['vix']:.1f} > 20: RISK-OFF {vix_penalty:+.3f}")

dxy_penalty = -market_data['dxy'] / 100 * 0.5
print(f"  DXY: +{market_data['dxy']:.1f}% → {dxy_penalty:+.3f}")

yields_penalty = -market_data['yields'] / 100 * 0.3
print(f"  Yields: +{market_data['yields']:.1f}% → {yields_penalty:+.3f}")

macro_score = vix_penalty + dxy_penalty + yields_penalty
print(f"  MACRO TOTAL: {macro_score:+.3f}")

# 7. INSTITUTIONAL (volume rising on decline)
print(f"\n7️⃣ INSTITUTIONAL FLOW:")
institutional_score = -0.06  # Selling detected
print(f"  Volume rising on decline: DISTRIBUTION {institutional_score:+.3f}")

# ========== APPLY WEIGHTS ==========
print(f"\n{'='*80}")
print("⚖️ APPLYING AVGO-SPECIFIC WEIGHTS:")
print("="*80)

weights = {
    'technical': 0.10,
    'institutional': 0.14,
    'news': 0.11,
    'futures': 0.11,
    'options': 0.11,
    'sector': 0.08,
    'vix': 0.06,
    'macro': 0.05,
}

weighted_scores = {
    'technical': technical_score * weights['technical'],
    'institutional': institutional_score * weights['institutional'],
    'options': options_score * weights['options'],
    'news': news_score * weights['news'],
    'sector': sector_score * weights['sector'],
    'futures': futures_score * weights['futures'],
    'vix': vix_penalty * weights['vix'],
    'macro': macro_score * weights['macro'],
}

for factor, score in weighted_scores.items():
    symbol = "🔴" if score < 0 else "🟢" if score > 0 else "⚪"
    print(f"  {symbol} {factor.capitalize():15s} {score:+.4f}")

total_score = sum(weighted_scores.values())
print(f"  {'─'*35}")
print(f"  {'TOTAL SCORE':17s} {total_score:+.4f}")

# Market regime (bearish)
market_regime = -0.025  # Bearish across the board
total_score += market_regime
print(f"  Market Regime:  {market_regime:+.4f}")
print(f"  {'─'*35}")
print(f"  {'FINAL SCORE':17s} {total_score:+.4f}")

# ========== DECISION ==========
print(f"\n{'='*80}")
print("🎯 SYSTEM DECISION LOGIC:")
print("="*80)

print(f"\nScore: {total_score:+.4f}")
print(f"Thresholds:")
print(f"  UP: > +0.04")
print(f"  DOWN: < -0.04")
print(f"  NEUTRAL: -0.04 to +0.04")

if total_score > 0.04:
    direction = "UP"
    color = "🟢"
elif total_score < -0.04:
    direction = "DOWN"
    color = "🔴"
else:
    direction = "NEUTRAL"
    color = "⚪"

print(f"\n{total_score:+.4f} {'<' if total_score < -0.04 else '>' if total_score > 0.04 else 'in'} {'DOWN threshold' if total_score < -0.04 else 'UP threshold' if total_score > 0.04 else 'NEUTRAL zone'}")
print(f"→ Direction: {color} {direction}")

# Confidence
confidence = 55 + abs(total_score) * 125
confidence = min(confidence, 95)
print(f"→ Confidence: {confidence:.1f}%")

trade_decision = "TRADE" if confidence >= 60 else "SKIP"
print(f"→ Trade Decision: {trade_decision} ({confidence:.1f}% {'≥' if confidence >= 60 else '<'} 60% threshold)")

# ========== PREDICTION ==========
print(f"\n{'='*80}")
print("🎯 FINAL PREDICTION:")
print("="*80)

print(f"\n{color} DIRECTION: {direction}")
print(f"📊 CONFIDENCE: {confidence:.1f}%")
print(f"📈 SCORE: {total_score:+.4f}")

# Calculate target
if direction == "DOWN":
    expected_move = abs(total_score) * 1.8
    target_price = stock_data['close'] * (1 - expected_move)
    range_low = stock_data['close'] * 0.97
    range_high = stock_data['close'] * 0.99
    
    print(f"\n💰 TARGET: ${target_price:.2f} (-{expected_move*100:.1f}%)")
    print(f"   Expected Range: ${range_low:.2f} - ${range_high:.2f}")
    print(f"   Key Support: $360 (heavy put activity)")
    
elif direction == "UP":
    expected_move = abs(total_score) * 1.8
    target_price = stock_data['close'] * (1 + expected_move)
    range_low = stock_data['close'] * 1.01
    range_high = stock_data['close'] * 1.03
    
    print(f"\n💰 TARGET: ${target_price:.2f} (+{expected_move*100:.1f}%)")
    print(f"   Expected Range: ${range_low:.2f} - ${range_high:.2f}")
else:
    print(f"\n💰 TARGET: ${stock_data['close']:.2f} (±0.5%)")
    print(f"   Expected Range: ${stock_data['close']*0.995:.2f} - ${stock_data['close']*1.005:.2f}")

# ========== REASONING ==========
print(f"\n{'='*80}")
print("💡 DETAILED REASONING:")
print("="*80)

print(f"\n🔴 BEARISH FACTORS:")
bearish = [
    f"News very negative ({news_score:+.3f}): AI delays + downgrades",
    f"Volume rising on decline ({volume_signal:+.3f}): DISTRIBUTION",
    f"5-day downtrend ({momentum:+.3f}): Momentum bearish",
    f"Options bearish (P/C {pcr:.2f}): Heavy put buying",
    f"Sector weak (SOX {market_data['sox_index']:+.1f}%)",
    f"Futures red (NASDAQ {market_data['nasdaq_futures']:+.1f}%)",
    f"VIX spiking ({market_data['vix']:.1f}): Risk-off",
    f"Macro headwinds (DXY +{market_data['dxy']:.1f}%, Yields +{market_data['yields']:.1f}%)",
]
for factor in bearish:
    print(f"  • {factor}")

print(f"\n🟢 BULLISH FACTORS:")
bullish = [
    f"RSI {rsi} approaching oversold (mild positive {rsi_signal:+.3f})",
    f"Close position {close_position:.0f}% (not at extremes)",
]
for factor in bullish:
    print(f"  • {factor}")

print(f"\n⚖️ THE BALANCE:")
print(f"  Bearish strength: 8 major factors aligned")
print(f"  Bullish strength: 1 minor factor (RSI approaching oversold)")
print(f"  Clear winner: {direction} (score {total_score:+.4f})")

print(f"\n🎲 RISK ASSESSMENT:")
if confidence >= 70:
    position = "75-100%"
    print(f"  ✅ HIGH CONFIDENCE ({confidence:.1f}%) - Standard position ({position})")
elif confidence >= 60:
    position = "50-75%"
    print(f"  ⚪ MODERATE CONFIDENCE ({confidence:.1f}%) - Partial position ({position})")
else:
    position = "25% or SKIP"
    print(f"  ⚠️ LOW CONFIDENCE ({confidence:.1f}%) - Small/skip ({position})")

# ========== TRADE PLAN ==========
if trade_decision == "TRADE":
    print(f"\n{'='*80}")
    print("📋 TRADE PLAN:")
    print("="*80)
    
    if direction == "DOWN":
        entry = stock_data['close']
        target = target_price
        stop = stock_data['close'] * 1.02
        risk = abs(entry - stop)
        reward = abs(entry - target)
        rr_ratio = reward / risk
        
        print(f"\n🔴 SHORT SETUP:")
        print(f"  Entry: ${entry:.2f} (market on close)")
        print(f"  Target: ${target:.2f} (-{((entry-target)/entry)*100:.1f}%)")
        print(f"  Stop: ${stop:.2f} (+2.0%)")
        print(f"  Risk: ${risk:.2f}")
        print(f"  Reward: ${reward:.2f}")
        print(f"  R:R Ratio: {rr_ratio:.2f}:1")
        print(f"  Position Size: {position}")
        print(f"\n  📊 Why trade:")
        print(f"     • Clear bearish alignment (8 factors)")
        print(f"     • High conviction ({confidence:.1f}%)")
        print(f"     • Distribution pattern confirmed")
        print(f"     • No countertrend signals")

print(f"\n{'='*80}")
print("CONCLUSION:")
print("="*80)
print(f"""
AVGO Analysis Summary:
────────────────────────────────────────

🔴 BEARISH SETUP CONFIRMED

Score: {total_score:+.4f} (strongly bearish)
Direction: {direction}
Confidence: {confidence:.1f}%

Why it's clear:
✅ News very negative (delays, downgrades)
✅ Distribution pattern (volume ↑ on price ↓)
✅ Bearish momentum continuing
✅ Options heavily bearish (P/C 1.35)
✅ Sector weakness (SOX -1.1%)
✅ Macro all bearish (VIX, DXY, Yields)
✅ No positive catalysts

Only mild counterargument:
⚠️ RSI 42 approaching oversold (but not there yet)

System Recommendation: {trade_decision}
Expected move: {'-2% to -3%' if direction == 'DOWN' else '+2% to +3%' if direction == 'UP' else '±0.5%'}
Key level: $360 support (heavy put activity)

This is a HIGH-QUALITY {direction} setup!
""")

print("="*80)
