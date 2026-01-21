"""
AVGO HIGH-VOLATILITY SURPRISE SCENARIO
Test system response to sudden VIX spike + major news
"""

print("="*80)
print("⚡ AVGO HIGH-VOLATILITY SURPRISE SCENARIO")
print("="*80)

# ========== INPUTS ==========
print("\n📊 SCENARIO DATA:")
print("="*80)

stock_data = {
    'symbol': 'AVGO',
    'close': 375.60,
    'intraday_low': 370.50,
    'intraday_high': 380.80,
    '5day_change': +1.2,
    'volume_trend': 'spiking',
    'rsi': 48,
}

market_data = {
    'nasdaq_futures': -1.2,
    'sox_index': +0.3,
    'vix': 25.4,  # MAJOR SPIKE!
    'dxy': +1.1,
    'yields': +1.5,
    'global_equities': -1.0,
}

options_data = {
    'put_call_ratio': 1.1,
    'large_calls': '385-390',
    'large_puts': '370-372',
}

news_sentiment = {
    'major_ai_delay': -0.20,  # MAJOR NEGATIVE
    'cloud_contracts': +0.05,
    'analyst_neutral': 0.00,
    'overall': -0.15,  # Net negative
}

print(f"Stock: {stock_data['symbol']}")
print(f"  Close: ${stock_data['close']:.2f}")
print(f"  Range: ${stock_data['intraday_low']:.2f} - ${stock_data['intraday_high']:.2f} (WIDE!)")
print(f"  5-Day: {stock_data['5day_change']:+.1f}%")
print(f"  Volume: {stock_data['volume_trend']} ⚡")
print(f"  RSI: {stock_data['rsi']} (neutral)")

print(f"\nMarket Environment:")
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% ⚠️ RISK-OFF")
print(f"  SOX: {market_data['sox_index']:+.1f}% (minor support)")
print(f"  VIX: {market_data['vix']:.1f} 🔥 MAJOR SPIKE!")
print(f"  DXY: {market_data['dxy']:+.1f}%")
print(f"  Yields: {market_data['yields']:+.1f}%")

print(f"\nOptions:")
print(f"  P/C Ratio: {options_data['put_call_ratio']:.2f} (slightly bearish)")
print(f"  Large Calls: ${options_data['large_calls']} (hedge)")
print(f"  Large Puts: ${options_data['large_puts']} (protection)")
print(f"  → STRADDLE positioning (uncertainty!)")

print(f"\nNews:")
print(f"  🚨 Major AI delay: {news_sentiment['major_ai_delay']:+.2f} (BREAKING)")
print(f"  ✅ Cloud contracts: {news_sentiment['cloud_contracts']:+.2f}")
print(f"  Overall: {news_sentiment['overall']:+.2f} (NET NEGATIVE)")

# ========== SYSTEM ANALYSIS ==========
print(f"\n{'='*80}")
print("🤖 SYSTEM ANALYSIS:")
print("="*80)

# 1. TECHNICAL
daily_range = stock_data['intraday_high'] - stock_data['intraday_low']
close_from_low = stock_data['close'] - stock_data['intraday_low']
close_position = (close_from_low / daily_range) * 100

print(f"\n1️⃣ TECHNICAL SIGNALS:")
print(f"  Intraday Range: ${daily_range:.2f} (10.3 points = HIGH VOLATILITY)")
print(f"  Close Position: {close_position:.0f}% of range")

if close_position > 60:
    close_signal = +0.03
    print(f"  → Closed near highs: Bullish (+0.03)")
elif close_position < 40:
    close_signal = -0.05
    print(f"  → Closed near lows: BEARISH (-0.05)")
else:
    close_signal = 0.00
    print(f"  → Mid-range: Neutral")

# RSI
rsi = stock_data['rsi']
if rsi > 45 and rsi < 55:
    rsi_signal = 0.00
    print(f"  RSI {rsi}: NEUTRAL (0.00)")
else:
    rsi_signal = 0.00
    print(f"  RSI {rsi}: Neutral")

# Momentum
momentum = stock_data['5day_change'] / 100 * 0.41
print(f"  5-Day Momentum: {stock_data['5day_change']:+.1f}% → {momentum:+.3f}")

# Volume spike
if stock_data['volume_trend'] == 'spiking':
    volume_signal = -0.06  # Usually bearish on bad news
    print(f"  Volume SPIKING: Likely on bad news {volume_signal:+.3f}")
else:
    volume_signal = 0.00

technical_score = close_signal + rsi_signal + momentum + volume_signal
print(f"  TECHNICAL TOTAL: {technical_score:+.3f}")

# 2. OPTIONS
print(f"\n2️⃣ OPTIONS SIGNALS:")
pcr = options_data['put_call_ratio']

if pcr > 1.5:
    options_score = +0.06
    print(f"  P/C {pcr:.2f} > 1.5: Excessive fear (contrarian)")
elif pcr > 1.2:
    options_score = -0.04
    print(f"  P/C {pcr:.2f} > 1.2: Bearish")
elif pcr < 1.0:
    options_score = +0.04
    print(f"  P/C {pcr:.2f} < 1.0: Bullish")
else:
    options_score = -0.02
    print(f"  P/C {pcr:.2f}: Slightly bearish")

# Straddle positioning
print(f"  Large calls AND puts: UNCERTAINTY/HEDGING")
print(f"  → Reflects high volatility expectations")

print(f"  OPTIONS TOTAL: {options_score:+.3f}")

# 3. NEWS
print(f"\n3️⃣ NEWS/FUNDAMENTAL:")
news_score = news_sentiment['overall']
print(f"  🚨 Major AI delay: {news_sentiment['major_ai_delay']:+.3f} (SIGNIFICANT)")
print(f"  Cloud wins: {news_sentiment['cloud_contracts']:+.3f} (positive offset)")
print(f"  NET: {news_score:+.3f} (NEGATIVE)")
print(f"  NEWS TOTAL: {news_score:+.3f}")

# 4. SECTOR
print(f"\n4️⃣ SECTOR (SOX):")
sector_score = market_data['sox_index'] / 100
print(f"  SOX: {market_data['sox_index']:+.1f}% → {sector_score:+.3f}")
print(f"  ⚠️ DIVERGENCE: Sector up but AVGO has bad news")
print(f"  SECTOR TOTAL: {sector_score:+.3f}")

# 5. FUTURES
print(f"\n5️⃣ FUTURES:")
futures_score = market_data['nasdaq_futures'] / 100 * 0.5
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% → {futures_score:+.3f}")
print(f"  🔴 RISK-OFF overnight")
print(f"  FUTURES TOTAL: {futures_score:+.3f}")

# 6. MACRO (HIGH IMPACT)
print(f"\n6️⃣ MACRO - MAJOR HEADWINDS:")
vix_impact = 0
if market_data['vix'] > 25:
    vix_impact = -0.06  # MAJOR risk-off
    print(f"  VIX {market_data['vix']:.1f} > 25: 🔥 PANIC SPIKE {vix_impact:+.3f}")
elif market_data['vix'] > 20:
    vix_impact = -0.04
    print(f"  VIX {market_data['vix']:.1f} > 20: Risk-off")
else:
    vix_impact = 0.00

dxy_impact = -market_data['dxy'] / 100 * 0.5
print(f"  DXY: +{market_data['dxy']:.1f}% → {dxy_impact:+.3f}")

yields_impact = -market_data['yields'] / 100 * 0.3
print(f"  Yields: +{market_data['yields']:.1f}% → {yields_impact:+.3f}")

macro_score = vix_impact + dxy_impact + yields_impact
print(f"  MACRO TOTAL: {macro_score:+.3f} ⚠️ SEVERE")

# 7. INSTITUTIONAL
print(f"\n7️⃣ INSTITUTIONAL:")
institutional_score = -0.04  # Volume spike on bad news = selling
print(f"  Volume spike on bad news: SELLING {institutional_score:+.3f}")

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
    symbol = "🔴" if score < -0.001 else "🟢" if score > 0.001 else "⚪"
    print(f"  {symbol} {factor.capitalize():15s} {score:+.4f}")

total_score = sum(weighted_scores.values())
print(f"  {'─'*35}")
print(f"  {'SUBTOTAL':17s} {total_score:+.4f}")

# Market regime (bearish)
market_regime = -0.025  # Risk-off
print(f"  Market Regime:  {market_regime:+.4f} (risk-off)")
total_score += market_regime
print(f"  {'─'*35}")
print(f"  {'FINAL SCORE':17s} {total_score:+.4f}")

# ========== VOLATILITY ADJUSTMENT ==========
print(f"\n{'='*80}")
print("⚡ VOLATILITY ADJUSTMENT:")
print("="*80)

vix = market_data['vix']
if vix > 25:
    vol_multiplier = 1.5
    confidence_penalty = 10
    print(f"  VIX {vix:.1f} > 25: EXTREME VOLATILITY")
    print(f"  → Score multiplier: {vol_multiplier}x (wider moves expected)")
    print(f"  → Confidence penalty: -{confidence_penalty}%")
elif vix > 20:
    vol_multiplier = 1.3
    confidence_penalty = 5
    print(f"  VIX {vix:.1f} > 20: High volatility")
else:
    vol_multiplier = 1.0
    confidence_penalty = 0
    print(f"  VIX {vix:.1f}: Normal")

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

# Confidence (with volatility penalty)
base_confidence = 55 + abs(total_score) * 125
base_confidence = min(base_confidence, 95)
adjusted_confidence = base_confidence - confidence_penalty
adjusted_confidence = max(adjusted_confidence, 45)

print(f"→ Base Confidence: {base_confidence:.1f}%")
print(f"→ VIX Penalty: -{confidence_penalty}%")
print(f"→ Adjusted Confidence: {adjusted_confidence:.1f}%")

# Trade decision
if adjusted_confidence >= 60:
    trade_decision = "TRADE (with caution)"
    position_size = "50% (volatility spike)"
elif adjusted_confidence >= 55:
    trade_decision = "TRADE (very small)"
    position_size = "25% (high uncertainty)"
else:
    trade_decision = "SKIP"
    position_size = "0% (too risky)"

print(f"→ Trade Decision: {trade_decision}")
print(f"→ Position Size: {position_size}")

# ========== PREDICTION ==========
print(f"\n{'='*80}")
print("🎯 FINAL PREDICTION:")
print("="*80)

print(f"\n{color} DIRECTION: {direction}")
print(f"📊 BASE CONFIDENCE: {base_confidence:.1f}%")
print(f"⚡ ADJUSTED CONFIDENCE: {adjusted_confidence:.1f}% (VIX penalty)")
print(f"📈 SCORE: {total_score:+.4f}")
print(f"💼 TRADE DECISION: {trade_decision}")
print(f"💰 POSITION SIZE: {position_size}")

# Target with volatility adjustment
if direction == "DOWN":
    expected_move = abs(total_score) * vol_multiplier * 1.8
    target = stock_data['close'] * (1 - expected_move)
    range_low = stock_data['close'] * 0.96
    range_high = stock_data['close'] * 0.99
    
    print(f"\n💰 TARGET: ${target:.2f} (-{expected_move*100:.1f}%)")
    print(f"   Expected Range: ${range_low:.2f} - ${range_high:.2f}")
    print(f"   HIGH VOLATILITY: Wider range expected")
    print(f"   Key Support: $370 (large puts)")
    
elif direction == "UP":
    expected_move = abs(total_score) * vol_multiplier * 1.8
    target = stock_data['close'] * (1 + expected_move)
    range_low = stock_data['close'] * 1.01
    range_high = stock_data['close'] * 1.04
    
    print(f"\n💰 TARGET: ${target:.2f} (+{expected_move*100:.1f}%)")
    print(f"   Expected Range: ${range_low:.2f} - ${range_high:.2f}")
else:
    range_low = stock_data['close'] * 0.97
    range_high = stock_data['close'] * 1.03
    print(f"\n💰 EXPECTED RANGE: ${range_low:.2f} - ${range_high:.2f}")
    print(f"   HIGH VOLATILITY: Wide range, unpredictable")

# ========== REASONING ==========
print(f"\n{'='*80}")
print("💡 DETAILED ANALYSIS:")
print("="*80)

print(f"\n🔴 BEARISH FACTORS:")
print(f"  • Major AI chip delay {news_sentiment['major_ai_delay']:+.2f} (SIGNIFICANT)")
print(f"  • NASDAQ futures {market_data['nasdaq_futures']:+.1f}% (risk-off)")
print(f"  • VIX spike to {market_data['vix']:.1f} (PANIC)")
print(f"  • Volume spiking on bad news (selling)")
print(f"  • DXY +{market_data['dxy']:.1f}%, Yields +{market_data['yields']:.1f}% (macro headwinds)")
print(f"  • Institutional selling detected")

print(f"\n🟢 BULLISH FACTORS:")
print(f"  • SOX +{market_data['sox_index']:.1f}% (sector support)")
print(f"  • Cloud contracts +{news_sentiment['cloud_contracts']:+.2f}")
print(f"  • 5-day momentum positive")

print(f"\n⚠️ HIGH UNCERTAINTY FACTORS:")
print(f"  • VIX {market_data['vix']:.1f} = Major volatility spike")
print(f"  • Options: Both calls AND puts (straddle)")
print(f"  • Wide intraday range ($10.30)")
print(f"  • Mixed signals (sector up, futures down)")

print(f"\n⚖️ THE BALANCE:")
print(f"  Score: {total_score:+.4f} ({direction})")
print(f"  BUT: VIX spike reduces confidence by {confidence_penalty}%")
print(f"  Result: {adjusted_confidence:.1f}% confidence")

# ========== RISK ASSESSMENT ==========
print(f"\n{'='*80}")
print("⚡ VOLATILITY RISK ASSESSMENT:")
print("="*80)

print(f"""
VIX Level: {market_data['vix']:.1f} (EXTREME)
Implications:
  ⚠️ Expect LARGER moves than normal
  ⚠️ Expect WHIPSAWS (direction changes)
  ⚠️ Lower confidence due to uncertainty
  ⚠️ Reduce position size by 50%
  ⚠️ Wider stops required

Options Positioning:
  Large calls at $385-390
  Large puts at $370-372
  → Market pricing in BOTH scenarios
  → Expect move to one of these levels

Recommendation:
  {trade_decision}
  Position: {position_size}
  {"Reduce size due to high vol" if vol_multiplier > 1.2 else "Normal sizing"}
""")

# ========== CONCLUSION ==========
print(f"\n{'='*80}")
print("CONCLUSION:")
print("="*80)

print(f"""
AVGO High-Volatility Analysis:
────────────────────────────────────────

{color} {direction} - {adjusted_confidence:.1f}% Confidence

Score: {total_score:+.4f}
VIX: {market_data['vix']:.1f} (EXTREME SPIKE!)

Why {direction}:
""")

if direction == "DOWN":
    print(f"""✅ BEARISH FACTORS DOMINATE:
  • Major negative catalyst (AI delay)
  • VIX spiking (market fear)
  • NASDAQ futures red
  • Volume spike on bad news
  • Macro all bearish

⚠️ BUT HIGH UNCERTAINTY:
  • Options pricing in volatility (straddle)
  • Sector slightly positive (divergence)
  • VIX spike = unpredictable moves

🎲 TRADE WITH EXTREME CAUTION:
  Position: {position_size}
  Expected: -2% to -4% (HIGH VOL)
  Stop: Wider due to volatility
  Key level: $370 (large puts)

⚡ VOLATILITY WARNING:
  Expect whipsaws and larger-than-normal moves.
  This is a HIGH-RISK setup despite clear catalyst.
""")
elif direction == "UP":
    print("Unexpected outcome given major negative catalyst")
else:
    print("Mixed signals + high volatility = No clear edge")

print("="*80)
