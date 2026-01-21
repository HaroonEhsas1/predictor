"""
AVGO STRONG BULLISH SCENARIO
Test if system can correctly identify and predict UP moves
"""

print("="*80)
print("🟢 AVGO STRONG BULLISH SCENARIO TEST")
print("="*80)

# ========== INPUTS ==========
print("\n📊 SCENARIO DATA:")
print("="*80)

stock_data = {
    'symbol': 'AVGO',
    'close': 368.50,
    'intraday_low': 365.00,
    'intraday_high': 370.80,
    '5day_change': +2.5,
    'volume_trend': 'rising_3_days',
    'rsi': 65,
}

market_data = {
    'nasdaq_futures': +0.5,
    'sox_index': +1.2,
    'vix': 17.8,
    'dxy': -0.4,
    'yields': +0.2,
    'global_equities': +0.8,
}

options_data = {
    'put_call_ratio': 0.75,
    'large_calls': '375-380',
    'puts_activity': 'very_light',
}

news_sentiment = {
    'strong_ai_orders': +0.15,
    'analyst_upgrades': +0.10,
    'positive_earnings_guidance': +0.08,
    'overall': +0.33,
}

print(f"Stock: {stock_data['symbol']}")
print(f"  Close: ${stock_data['close']:.2f}")
print(f"  Range: ${stock_data['intraday_low']:.2f} - ${stock_data['intraday_high']:.2f}")
print(f"  5-Day: {stock_data['5day_change']:+.1f}% 📈 UPTREND")
print(f"  Volume: {stock_data['volume_trend']} 🟢 ACCUMULATION")
print(f"  RSI: {stock_data['rsi']} (strong momentum)")

print(f"\nMarket Environment:")
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% 🟢")
print(f"  SOX: {market_data['sox_index']:+.1f}% 🚀 STRONG SECTOR")
print(f"  VIX: {market_data['vix']:.1f} (low volatility)")
print(f"  DXY: {market_data['dxy']:+.1f}% (weak dollar = bullish)")
print(f"  Yields: {market_data['yields']:+.1f}% (neutral)")

print(f"\nOptions:")
print(f"  P/C Ratio: {options_data['put_call_ratio']:.2f} 🚀 VERY BULLISH")
print(f"  Large Calls: ${options_data['large_calls']}")
print(f"  Puts: {options_data['puts_activity']}")

print(f"\nNews:")
print(f"  🚀 Strong AI orders: {news_sentiment['strong_ai_orders']:+.2f}")
print(f"  📈 Analyst upgrades: {news_sentiment['analyst_upgrades']:+.2f}")
print(f"  💰 Earnings guidance: {news_sentiment['positive_earnings_guidance']:+.2f}")
print(f"  Overall: {news_sentiment['overall']:+.2f} 🔥 VERY POSITIVE")

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
    close_signal = +0.06
    print(f"  → Closed near highs: BULLISH (+0.06)")
elif close_position < 40:
    close_signal = -0.04
    print(f"  → Closed near lows: Bearish")
else:
    close_signal = 0.00
    print(f"  → Mid-range: Neutral")

# RSI
rsi = stock_data['rsi']
if rsi > 70:
    rsi_signal = -0.06
    print(f"  RSI {rsi}: OVERBOUGHT (reversal risk) -0.06")
elif rsi > 65:
    rsi_signal = +0.02
    print(f"  RSI {rsi}: Strong momentum (not extreme yet) +0.02")
elif rsi > 55:
    rsi_signal = +0.04
    print(f"  RSI {rsi}: Bullish +0.04")
elif rsi < 30:
    rsi_signal = +0.08
    print(f"  RSI {rsi}: Oversold bounce")
else:
    rsi_signal = 0.00
    print(f"  RSI {rsi}: Neutral")

# Momentum
momentum = stock_data['5day_change'] / 100 * 0.41
print(f"  5-Day Momentum: {stock_data['5day_change']:+.1f}% → {momentum:+.3f} 📈")

# Volume (rising = accumulation)
if stock_data['volume_trend'] == 'rising_3_days':
    volume_signal = +0.08
    print(f"  Volume Rising 3 Days: ACCUMULATION! {volume_signal:+.3f} 🟢")
else:
    volume_signal = 0.00

technical_score = close_signal + rsi_signal + momentum + volume_signal
print(f"  TECHNICAL TOTAL: {technical_score:+.3f}")

# 2. OPTIONS
print(f"\n2️⃣ OPTIONS SIGNALS:")
pcr = options_data['put_call_ratio']

if pcr < 0.8:
    options_score = +0.12
    print(f"  P/C {pcr:.2f} < 0.8: VERY BULLISH (call heavy) +0.12")
elif pcr < 1.0:
    options_score = +0.06
    print(f"  P/C {pcr:.2f} < 1.0: Bullish")
elif pcr > 1.5:
    options_score = +0.04
    print(f"  P/C {pcr:.2f} > 1.5: Contrarian bullish")
else:
    options_score = 0.00

# Large calls
print(f"  Large calls at ${options_data['large_calls']}: Bullish targets")
options_score += 0.03

print(f"  OPTIONS TOTAL: {options_score:+.3f}")

# 3. NEWS
print(f"\n3️⃣ NEWS/FUNDAMENTAL:")
news_score = news_sentiment['overall']
print(f"  🚀 Strong AI orders: {news_sentiment['strong_ai_orders']:+.3f}")
print(f"  📈 Analyst upgrades: {news_sentiment['analyst_upgrades']:+.3f}")
print(f"  💰 Earnings guidance: {news_sentiment['positive_earnings_guidance']:+.3f}")
print(f"  NEWS TOTAL: {news_score:+.3f} 🔥")

# 4. SECTOR
print(f"\n4️⃣ SECTOR (SOX):")
sector_score = market_data['sox_index'] / 100
print(f"  SOX: {market_data['sox_index']:+.1f}% → {sector_score:+.3f} 🚀")
print(f"  SECTOR TOTAL: {sector_score:+.3f}")

# 5. FUTURES
print(f"\n5️⃣ FUTURES:")
futures_score = market_data['nasdaq_futures'] / 100 * 0.5
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% → {futures_score:+.3f} 🟢")
print(f"  FUTURES TOTAL: {futures_score:+.3f}")

# 6. MACRO
print(f"\n6️⃣ MACRO ENVIRONMENT:")
vix_impact = 0
if market_data['vix'] < 18:
    vix_impact = +0.03
    print(f"  VIX {market_data['vix']:.1f} < 18: Low volatility (risk-on) {vix_impact:+.3f}")
elif market_data['vix'] > 20:
    vix_impact = -0.03
    print(f"  VIX {market_data['vix']:.1f} > 20: Risk-off")
else:
    vix_impact = 0.00
    print(f"  VIX {market_data['vix']:.1f}: Neutral")

# Weak dollar = bullish for tech
dxy_impact = -market_data['dxy'] / 100 * 0.5
print(f"  DXY: {market_data['dxy']:+.1f}% → {dxy_impact:+.3f} (weak dollar = bullish)")

yields_impact = -market_data['yields'] / 100 * 0.3
print(f"  Yields: {market_data['yields']:+.1f}% → {yields_impact:+.3f}")

macro_score = vix_impact + dxy_impact + yields_impact
print(f"  MACRO TOTAL: {macro_score:+.3f}")

# 7. INSTITUTIONAL
print(f"\n7️⃣ INSTITUTIONAL FLOW:")
institutional_score = +0.06  # Rising volume = accumulation
print(f"  Volume rising 3 days: ACCUMULATION {institutional_score:+.3f} 🟢")

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
    'vix': vix_impact * weights['vix'],
    'macro': macro_score * weights['macro'],
}

for factor, score in weighted_scores.items():
    symbol = "🔴" if score < 0 else "🟢" if score > 0 else "⚪"
    print(f"  {symbol} {factor.capitalize():15s} {score:+.4f}")

total_score = sum(weighted_scores.values())
print(f"  {'─'*35}")
print(f"  {'SUBTOTAL':17s} {total_score:+.4f}")

# Market regime (bullish)
market_regime = +0.025  # Strong bullish
print(f"  Market Regime:  {market_regime:+.4f} (bullish)")
total_score += market_regime
print(f"  {'─'*35}")
print(f"  {'FINAL SCORE':17s} {total_score:+.4f}")

# ========== DECISION ==========
print(f"\n{'='*80}")
print("🎯 SYSTEM DECISION LOGIC:")
print("="*80)

print(f"\nScore: {total_score:+.4f}")
print(f"Thresholds: UP > +0.04, DOWN < -0.04")

if total_score > 0.04:
    direction = "UP"
    color = "🟢"
elif total_score < -0.04:
    direction = "DOWN"
    color = "🔴"
else:
    direction = "NEUTRAL"
    color = "⚪"

print(f"\n{total_score:+.4f} {'>' if total_score > 0.04 else '<' if total_score < -0.04 else 'in'} threshold")
print(f"→ Direction: {color} {direction}")

# Confidence
confidence = 55 + abs(total_score) * 125
confidence = min(confidence, 95)

print(f"→ Confidence: {confidence:.1f}%")

# Trade decision
if confidence >= 60:
    trade_decision = "TRADE"
    if confidence >= 75:
        position_size = "100% (high conviction)"
    elif confidence >= 65:
        position_size = "75% (good setup)"
    else:
        position_size = "50-75% (decent)"
else:
    trade_decision = "SKIP"
    position_size = "0%"

print(f"→ Trade Decision: {trade_decision}")
print(f"→ Position Size: {position_size}")

# ========== PREDICTION ==========
print(f"\n{'='*80}")
print("🎯 FINAL PREDICTION:")
print("="*80)

print(f"\n{color} DIRECTION: {direction}")
print(f"📊 CONFIDENCE: {confidence:.1f}%")
print(f"📈 SCORE: {total_score:+.4f}")
print(f"💼 TRADE DECISION: {trade_decision}")
print(f"💰 POSITION SIZE: {position_size}")

# Target
if direction == "UP":
    expected_move = abs(total_score) * 1.5
    target = stock_data['close'] * (1 + expected_move)
    range_low = stock_data['close'] * 1.01
    range_high = stock_data['close'] * 1.03
    
    print(f"\n💰 TARGET: ${target:.2f} (+{expected_move*100:.1f}%)")
    print(f"   Expected Range: ${range_low:.2f} - ${range_high:.2f}")
    print(f"   Key Resistance: $375-380 (large call activity)")
    
elif direction == "DOWN":
    expected_move = abs(total_score) * 1.5
    target = stock_data['close'] * (1 - expected_move)
    print(f"\n💰 TARGET: ${target:.2f} (-{expected_move*100:.1f}%)")
else:
    print(f"\n💰 TARGET: ${stock_data['close']:.2f} (±0.5%)")

# ========== REASONING ==========
print(f"\n{'='*80}")
print("💡 SIGNAL BREAKDOWN:")
print("="*80)

print(f"\n🟢 BULLISH FACTORS (ALL ALIGNED!):")
print(f"  • News VERY positive ({news_score:+.3f}): AI orders, upgrades, earnings")
print(f"  • Options VERY bullish ({options_score:+.3f}): P/C 0.75, large calls")
print(f"  • Volume rising 3 days ({volume_signal:+.3f}): Accumulation")
print(f"  • Sector strong (SOX {market_data['sox_index']:+.1f}%)")
print(f"  • Momentum positive (+{stock_data['5day_change']:.1f}% 5-day)")
print(f"  • Technical strong (RSI {rsi}, closed near highs)")
print(f"  • Futures bullish (NASDAQ {market_data['nasdaq_futures']:+.1f}%)")
print(f"  • Macro supportive (VIX low, dollar weak)")
print(f"  • Institutional accumulation detected")

print(f"\n🔴 BEARISH FACTORS:")
print(f"  • None detected!")

print(f"\n⚪ NEUTRAL/CAUTION:")
print(f"  • RSI 65 approaching overbought (but momentum strong)")

print(f"\n⚖️ THE VERDICT:")
print(f"  9 bullish factors aligned")
print(f"  0 bearish factors")
print(f"  Score: {total_score:+.4f} (STRONG {direction})")
print(f"  Confidence: {confidence:.1f}%")

# ========== TRADE PLAN ==========
if trade_decision == "TRADE":
    print(f"\n{'='*80}")
    print("📋 TRADE PLAN:")
    print("="*80)
    
    entry = stock_data['close']
    target_price = target
    stop = stock_data['close'] * 0.98
    risk = abs(entry - stop)
    reward = abs(target_price - entry)
    rr_ratio = reward / risk
    
    print(f"\n🟢 LONG SETUP:")
    print(f"  Entry: ${entry:.2f} (market on close)")
    print(f"  Target: ${target_price:.2f} (+{((target_price-entry)/entry)*100:.1f}%)")
    print(f"  Stop: ${stop:.2f} (-2.0%)")
    print(f"  Risk: ${risk:.2f}")
    print(f"  Reward: ${reward:.2f}")
    print(f"  R:R Ratio: {rr_ratio:.2f}:1")
    print(f"  Position Size: {position_size}")
    
    print(f"\n  📊 Why trade:")
    print(f"     • Perfect bullish alignment (9 factors)")
    print(f"     • Very high conviction ({confidence:.1f}%)")
    print(f"     • Strong catalysts (AI orders, upgrades, earnings)")
    print(f"     • No conflicting signals")
    print(f"     • Low volatility environment (VIX {market_data['vix']:.1f})")
    
    print(f"\n  🎯 Probability Assessment:")
    print(f"     • Confidence {confidence:.1f}% suggests:")
    if confidence >= 75:
        print(f"       - Very high probability of target hit")
        print(f"       - Consider trailing stop")
        print(f"       - May exceed target ($375-380)")
    elif confidence >= 65:
        print(f"       - Good probability of target hit")
        print(f"       - Use standard stops")
    else:
        print(f"       - Decent probability")
        print(f"       - Reduce position size")

# ========== CONCLUSION ==========
print(f"\n{'='*80}")
print("CONCLUSION:")
print("="*80)

print(f"""
AVGO Strong Bullish Analysis:
────────────────────────────────────────

{color} {direction} - {confidence:.1f}% Confidence

Score: {total_score:+.4f} (very strong)

Why {direction}:
""")

if direction == "UP":
    print(f"""✅ PERFECT BULLISH ALIGNMENT:
  • 9 factors all bullish
  • 0 bearish factors
  • Score {total_score:+.4f} >> +0.04 threshold

🔥 CATALYSTS:
  • Strong AI chip orders (major positive)
  • Analyst upgrades 5-7% (validation)
  • Positive earnings guidance (tomorrow catalyst)

📊 TECHNICAL CONFIRMATION:
  • Volume rising 3 days (smart money buying)
  • RSI 65 (strong but not extreme)
  • Closed near highs (strength)
  • 5-day uptrend continuing

💰 OPTIONS CONFIRM:
  • P/C 0.75 (very bullish)
  • Large calls $375-380 (targets identified)
  • Very light puts (no hedging)

🌍 MACRO SUPPORTIVE:
  • SOX +1.2% (sector strength)
  • NASDAQ +0.5% (market strength)
  • VIX 17.8 (low volatility)
  • Dollar weak (bullish for tech)

🎯 THIS IS A HIGH-QUALITY SETUP!
Expected: +1% to +3%
Target: $375-380 range
Position: {position_size}

{f"⚠️ Only caution: RSI 65 (watch for profit-taking)" if rsi >= 65 else ""}
""")
elif direction == "DOWN":
    print("Unexpected outcome given all bullish factors")
else:
    print("Unexpected NEUTRAL given strong bullish setup")

print("="*80)
