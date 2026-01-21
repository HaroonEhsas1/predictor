"""
AVGO MIXED SIGNALS STRESS TEST
Can the system handle conflicting data without forcing UP/DOWN?
"""

print("="*80)
print("⚪ AVGO MIXED SIGNALS STRESS TEST")
print("="*80)

# ========== INPUTS ==========
print("\n📊 SCENARIO DATA:")
print("="*80)

stock_data = {
    'symbol': 'AVGO',
    'close': 378.20,
    'intraday_low': 374.50,
    'intraday_high': 380.80,
    '5day_change': +0.5,
    'volume_trend': 'flat',
    'rsi': 50,
}

market_data = {
    'nasdaq_futures': +0.2,
    'sox_index': -0.5,
    'vix': 19.5,
    'dxy': +0.5,
    'yields': +0.3,
    'global_equities': +0.3,
}

options_data = {
    'put_call_ratio': 1.05,
    'large_calls': '385-390',
    'moderate_puts': '370-375',
}

news_sentiment = {
    'ai_chip_delay_minor': -0.03,
    'analysts_reaffirm': 0.00,
    'cloud_contract_wins': +0.05,
    'overall': +0.02,  # Slightly positive
}

print(f"Stock: {stock_data['symbol']}")
print(f"  Close: ${stock_data['close']:.2f}")
print(f"  Range: ${stock_data['intraday_low']:.2f} - ${stock_data['intraday_high']:.2f}")
print(f"  5-Day: {stock_data['5day_change']:+.1f}%")
print(f"  Volume: {stock_data['volume_trend']}")
print(f"  RSI: {stock_data['rsi']} (NEUTRAL)")

print(f"\nMarket Environment:")
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% (slightly bullish)")
print(f"  SOX: {market_data['sox_index']:+.1f}% (slightly weak)")
print(f"  VIX: {market_data['vix']:.1f} (moderate)")
print(f"  DXY: {market_data['dxy']:+.1f}%")
print(f"  Yields: {market_data['yields']:+.1f}%")

print(f"\nOptions:")
print(f"  P/C Ratio: {options_data['put_call_ratio']:.2f} (NEUTRAL)")
print(f"  Large Calls: ${options_data['large_calls']}")
print(f"  Moderate Puts: ${options_data['moderate_puts']}")

print(f"\nNews:")
print(f"  Minor AI delay: {news_sentiment['ai_chip_delay_minor']:+.2f}")
print(f"  Analysts reaffirm: {news_sentiment['analysts_reaffirm']:+.2f}")
print(f"  Cloud contracts: {news_sentiment['cloud_contract_wins']:+.2f}")
print(f"  Overall: {news_sentiment['overall']:+.2f} (slightly positive)")

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
    print(f"  → Near highs: Bullish (+0.04)")
elif close_position < 40:
    close_signal = -0.04
    print(f"  → Near lows: Bearish (-0.04)")
else:
    close_signal = 0.00
    print(f"  → Mid-range: NEUTRAL (0.00)")

# RSI
rsi = stock_data['rsi']
if rsi > 45 and rsi < 55:
    rsi_signal = 0.00
    print(f"  RSI {rsi}: NEUTRAL ZONE (0.00)")
elif rsi < 30:
    rsi_signal = +0.08
    print(f"  RSI {rsi}: Oversold +0.08")
elif rsi > 70:
    rsi_signal = -0.08
    print(f"  RSI {rsi}: Overbought -0.08")
elif rsi < 45:
    rsi_signal = +0.03
    print(f"  RSI {rsi}: Mild bullish +0.03")
else:
    rsi_signal = -0.03
    print(f"  RSI {rsi}: Mild bearish -0.03")

# Momentum
momentum = stock_data['5day_change'] / 100 * 0.41
print(f"  5-Day Momentum: {stock_data['5day_change']:+.1f}% → {momentum:+.3f}")

# Volume
volume_signal = 0.00
print(f"  Volume Flat: NEUTRAL (0.00)")

technical_score = close_signal + rsi_signal + momentum + volume_signal
print(f"  TECHNICAL TOTAL: {technical_score:+.3f}")

# 2. OPTIONS
print(f"\n2️⃣ OPTIONS SIGNALS:")
pcr = options_data['put_call_ratio']

if pcr > 1.5:
    options_score = +0.06
    print(f"  P/C {pcr:.2f} > 1.5: Excessive fear (contrarian bullish)")
elif pcr > 1.2:
    options_score = -0.05
    print(f"  P/C {pcr:.2f} > 1.2: Bearish")
elif pcr < 0.8:
    options_score = +0.08
    print(f"  P/C {pcr:.2f} < 0.8: Bullish")
elif pcr < 1.0:
    options_score = +0.03
    print(f"  P/C {pcr:.2f} < 1.0: Slightly bullish")
else:
    options_score = 0.00
    print(f"  P/C {pcr:.2f}: NEUTRAL")

# Large calls vs moderate puts
if 'large_calls' in options_data:
    options_score += 0.02
    print(f"  Large calls present: +0.02 (bullish bias)")

print(f"  OPTIONS TOTAL: {options_score:+.3f}")

# 3. NEWS
print(f"\n3️⃣ NEWS/FUNDAMENTAL:")
news_score = news_sentiment['overall']
print(f"  Minor AI delay: {news_sentiment['ai_chip_delay_minor']:+.3f}")
print(f"  Cloud contracts: {news_sentiment['cloud_contract_wins']:+.3f}")
print(f"  Analysts neutral: {news_sentiment['analysts_reaffirm']:+.3f}")
print(f"  NET: {news_score:+.3f} (slightly positive)")
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
print(f"\n6️⃣ MACRO:")
vix_impact = 0
if market_data['vix'] > 20:
    vix_impact = -0.03
    print(f"  VIX {market_data['vix']:.1f} > 20: Slight risk-off")
elif market_data['vix'] < 15:
    vix_impact = +0.02
    print(f"  VIX {market_data['vix']:.1f} < 15: Risk-on")
else:
    vix_impact = 0.00
    print(f"  VIX {market_data['vix']:.1f}: NEUTRAL")

dxy_impact = -market_data['dxy'] / 100 * 0.5
print(f"  DXY: +{market_data['dxy']:.1f}% → {dxy_impact:+.3f}")

yields_impact = -market_data['yields'] / 100 * 0.3
print(f"  Yields: +{market_data['yields']:.1f}% → {yields_impact:+.3f}")

macro_score = vix_impact + dxy_impact + yields_impact
print(f"  MACRO TOTAL: {macro_score:+.3f}")

# 7. INSTITUTIONAL
print(f"\n7️⃣ INSTITUTIONAL:")
institutional_score = 0.00
print(f"  Volume flat (no accumulation/distribution): {institutional_score:+.3f}")

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

# Market regime (neutral)
market_regime = 0.00  # Mixed signals
print(f"  Market Regime:  {market_regime:+.4f} (mixed)")
total_score += market_regime
print(f"  {'─'*35}")
print(f"  {'FINAL SCORE':17s} {total_score:+.4f}")

# ========== DECISION ==========
print(f"\n{'='*80}")
print("🎯 SYSTEM DECISION LOGIC:")
print("="*80)

print(f"\nScore: {total_score:+.4f}")
print(f"\nDecision Thresholds:")
print(f"  UP:      score > +0.04")
print(f"  DOWN:    score < -0.04")
print(f"  NEUTRAL: -0.04 to +0.04 (DEADZONE)")

print(f"\n{'─'*50}")
print(f"Score Analysis:")
if total_score > 0.04:
    zone = "BULLISH ZONE"
    direction = "UP"
    color = "🟢"
elif total_score < -0.04:
    zone = "BEARISH ZONE"
    direction = "DOWN"
    color = "🔴"
else:
    zone = "NEUTRAL DEADZONE"
    direction = "NEUTRAL"
    color = "⚪"

print(f"  {total_score:+.4f} is in the {zone}")
print(f"  → Direction: {color} {direction}")

# Confidence
confidence = 55 + abs(total_score) * 125
confidence = min(confidence, 95)
print(f"  → Confidence: {confidence:.1f}%")

# Trade decision
if direction == "NEUTRAL":
    trade_decision = "SKIP"
    reason = "Mixed signals - no clear edge"
elif confidence >= 60:
    trade_decision = "TRADE"
    reason = f"Confidence {confidence:.1f}% ≥ 60%"
else:
    trade_decision = "SKIP"
    reason = f"Confidence {confidence:.1f}% < 60%"

print(f"  → Trade Decision: {trade_decision}")
print(f"  → Reason: {reason}")

# ========== PREDICTION ==========
print(f"\n{'='*80}")
print("🎯 FINAL PREDICTION:")
print("="*80)

print(f"\n{color} DIRECTION: {direction}")
print(f"📊 CONFIDENCE: {confidence:.1f}%")
print(f"📈 SCORE: {total_score:+.4f}")
print(f"💼 TRADE DECISION: {trade_decision}")

# Target
if direction == "NEUTRAL":
    range_low = stock_data['close'] * 0.995
    range_high = stock_data['close'] * 1.005
    print(f"\n💰 EXPECTED RANGE: ${range_low:.2f} - ${range_high:.2f}")
    print(f"   Movement: ±0.5% (choppy/sideways)")
    print(f"   Key Levels:")
    print(f"     Support: $375 (moderate puts)")
    print(f"     Resistance: $385 (large calls)")
elif direction == "UP":
    expected_move = abs(total_score) * 1.5
    target = stock_data['close'] * (1 + expected_move)
    print(f"\n💰 TARGET: ${target:.2f} (+{expected_move*100:.1f}%)")
else:
    expected_move = abs(total_score) * 1.5
    target = stock_data['close'] * (1 - expected_move)
    print(f"\n💰 TARGET: ${target:.2f} (-{expected_move*100:.1f}%)")

# ========== REASONING ==========
print(f"\n{'='*80}")
print("💡 SIGNAL BREAKDOWN:")
print("="*80)

bullish_signals = []
bearish_signals = []
neutral_signals = []

if technical_score > 0.001:
    bullish_signals.append(f"Technical +{technical_score:.3f}")
elif technical_score < -0.001:
    bearish_signals.append(f"Technical {technical_score:.3f}")
else:
    neutral_signals.append(f"Technical {technical_score:.3f}")

if options_score > 0.001:
    bullish_signals.append(f"Options +{options_score:.3f}")
elif options_score < -0.001:
    bearish_signals.append(f"Options {options_score:.3f}")
else:
    neutral_signals.append(f"Options {options_score:.3f}")

if news_score > 0.001:
    bullish_signals.append(f"News +{news_score:.3f}")
elif news_score < -0.001:
    bearish_signals.append(f"News {news_score:.3f}")
else:
    neutral_signals.append(f"News {news_score:.3f}")

if sector_score > 0.001:
    bullish_signals.append(f"Sector +{sector_score:.3f}")
elif sector_score < -0.001:
    bearish_signals.append(f"Sector {sector_score:.3f}")
else:
    neutral_signals.append(f"Sector {sector_score:.3f}")

if futures_score > 0.001:
    bullish_signals.append(f"Futures +{futures_score:.3f}")
elif futures_score < -0.001:
    bearish_signals.append(f"Futures {futures_score:.3f}")
else:
    neutral_signals.append(f"Futures {futures_score:.3f}")

if macro_score > 0.001:
    bullish_signals.append(f"Macro +{macro_score:.3f}")
elif macro_score < -0.001:
    bearish_signals.append(f"Macro {macro_score:.3f}")
else:
    neutral_signals.append(f"Macro {macro_score:.3f}")

print(f"\n🟢 BULLISH SIGNALS ({len(bullish_signals)}):")
if bullish_signals:
    for signal in bullish_signals:
        print(f"  • {signal}")
else:
    print(f"  • None")

print(f"\n🔴 BEARISH SIGNALS ({len(bearish_signals)}):")
if bearish_signals:
    for signal in bearish_signals:
        print(f"  • {signal}")
else:
    print(f"  • None")

print(f"\n⚪ NEUTRAL SIGNALS ({len(neutral_signals)}):")
if neutral_signals:
    for signal in neutral_signals:
        print(f"  • {signal}")
else:
    print(f"  • None")

print(f"\n📊 SIGNAL BALANCE:")
print(f"  Bullish: {len(bullish_signals)}")
print(f"  Bearish: {len(bearish_signals)}")
print(f"  Neutral: {len(neutral_signals)}")
print(f"  Net Score: {total_score:+.4f}")

if direction == "NEUTRAL":
    print(f"\n✅ SYSTEM CORRECTLY IDENTIFIED MIXED SIGNALS!")
    print(f"   No forced prediction - honest assessment")

# ========== CONCLUSION ==========
print(f"\n{'='*80}")
print("CONCLUSION:")
print("="*80)

print(f"""
AVGO Mixed-Signal Analysis:
────────────────────────────────────────

{color} {direction} - {confidence:.1f}% Confidence

Score: {total_score:+.4f} (in neutral zone)

Signal Distribution:
  🟢 Bullish: {len(bullish_signals)}
  🔴 Bearish: {len(bearish_signals)}
  ⚪ Neutral: {len(neutral_signals)}

Why {direction}:
""")

if direction == "NEUTRAL":
    print("""✅ CORRECTLY DETECTED MIXED SIGNALS:
  • RSI 50 (neutral)
  • Close mid-range
  • P/C 1.05 (neutral)
  • News mixed (delay vs wins)
  • Macro mixed (NASDAQ up, SOX down)
  • Volume flat (no conviction)

⚪ No clear edge detected
⚪ System refuses to force direction
⚪ Recommends SKIP trade

This is SMART risk management!
Expected: Choppy, range-bound ($375-385)

✅ STRESS TEST PASSED!
System showed DISCIPLINE by not overtrading.
""")
else:
    print(f"""
Dominant factors pushing {direction}:
  {', '.join(bullish_signals if direction == 'UP' else bearish_signals)}

Trade with CAUTION - confidence only {confidence:.1f}%
""")

print("="*80)
