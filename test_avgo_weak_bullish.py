"""
AVGO WEAK BULLISH SCENARIO
Testing system response to mild optimism with neutral technicals
Classic "maybe trade, maybe skip" situation
"""

print("="*80)
print("📊 AVGO WEAK BULLISH SCENARIO - SYSTEM LOGIC TEST")
print("="*80)

# ========== INPUTS ==========
print("\n📊 SCENARIO DATA:")
print("="*80)

stock_data = {
    'symbol': 'AVGO',
    'close': 398.70,
    'intraday_low': 394.20,
    'intraday_high': 401.30,
    '5day_trend': 'choppy_slight_up',  # Up after 4-day decline
    'volume_trend': 'average',
    'rsi': 54,
    'macd': 'weak_bullish_cross',
    'sma_20': 'flat',
    'price_vs_sma_50': 'hugging',
}

market_data = {
    'nasdaq_futures': +0.4,
    'sox_index': +0.1,
    'vix': 17.8,
    'dxy': -0.3,
    'yields': 0.0,  # Steady
    'tech_recovery': 'mild',
}

options_data = {
    'put_call_ratio': 0.95,
    'call_activity_405': 'notable',
    'call_activity_410': 'notable',
    'puts_390': 'minor',
}

news_sentiment = {
    'ai_partnership': +0.03,  # Small positive
    'analyst_view': 'fair valuation, limited momentum',
    'overall': +0.02,  # Slightly positive
}

print(f"Stock: {stock_data['symbol']}")
print(f"  Close: ${stock_data['close']:.2f}")
print(f"  Range: ${stock_data['intraday_low']:.2f} - ${stock_data['intraday_high']:.2f}")
print(f"  5-Day: {stock_data['5day_trend']}")
print(f"  Volume: {stock_data['volume_trend']}")
print(f"  RSI: {stock_data['rsi']} (NEUTRAL)")
print(f"  MACD: {stock_data['macd']}")

print(f"\nMarket Context:")
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% (mild optimism)")
print(f"  SOX: {market_data['sox_index']:+.1f}% (flat)")
print(f"  VIX: {market_data['vix']:.1f} (moderate calm)")
print(f"  DXY: {market_data['dxy']:+.1f}% (weak dollar)")
print(f"  Yields: steady")

print(f"\nOptions:")
print(f"  P/C Ratio: {options_data['put_call_ratio']:.2f} (BALANCED)")
print(f"  Calls at $405-410: Notable activity")
print(f"  Puts at $390: Minor protection")

print(f"\nNews:")
print(f"  AI partnership: {news_sentiment['ai_partnership']:+.2f}")
print(f"  Analyst view: {news_sentiment['analyst_view']}")
print(f"  Overall: {news_sentiment['overall']:+.2f} (SLIGHTLY POSITIVE)")

# ========== SYSTEM ANALYSIS ==========
print(f"\n{'='*80}")
print("🤖 SYSTEM ANALYSIS (USING ACTUAL LOGIC):")
print("="*80)

# 1. TECHNICAL
daily_range = stock_data['intraday_high'] - stock_data['intraday_low']
close_from_low = stock_data['close'] - stock_data['intraday_low']
close_position = (close_from_low / daily_range) * 100

print(f"\n1️⃣ TECHNICAL SIGNALS:")
print(f"  Close Position: {close_position:.0f}% of range")

if close_position > 60:
    close_signal = +0.04
    print(f"  → Closed near highs: Bullish (+0.04)")
elif close_position < 40:
    close_signal = -0.04
    print(f"  → Closed near lows: Bearish (-0.04)")
else:
    close_signal = 0.00
    print(f"  → Mid-range: NEUTRAL (0.00)")

# RSI 54 = neutral
rsi = stock_data['rsi']
if rsi >= 45 and rsi <= 55:
    rsi_signal = 0.00
    print(f"  RSI {rsi}: NEUTRAL ZONE (0.00)")
else:
    rsi_signal = 0.00

# MACD weak bullish cross
macd_signal = +0.02
print(f"  MACD: Weak bullish cross +0.02")

# Choppy trend
momentum_signal = +0.001  # Slight up after decline
print(f"  5-Day Trend: Choppy/slight up → {momentum_signal:+.3f}")

# Average volume = neutral
volume_signal = 0.00
print(f"  Volume Average: NEUTRAL (0.00)")

technical_score = close_signal + rsi_signal + macd_signal + momentum_signal + volume_signal
print(f"  TECHNICAL TOTAL: {technical_score:+.3f}")

# 2. OPTIONS
print(f"\n2️⃣ OPTIONS SIGNALS:")
pcr = options_data['put_call_ratio']

if pcr < 1.0:
    options_score = +0.02
    print(f"  P/C {pcr:.2f} < 1.0: Slightly bullish +0.02")
else:
    options_score = 0.00

# Notable calls at 405-410
print(f"  Calls at $405-410: Targets above current price")
options_score += 0.01

print(f"  OPTIONS TOTAL: {options_score:+.3f}")

# 3. NEWS
print(f"\n3️⃣ NEWS/FUNDAMENTAL:")
news_score = news_sentiment['overall']
print(f"  AI partnership: {news_sentiment['ai_partnership']:+.3f} (minor)")
print(f"  Analyst: Fair valuation, limited momentum (neutral)")
print(f"  NEWS TOTAL: {news_score:+.3f}")

# 4. SECTOR
print(f"\n4️⃣ SECTOR (SOX):")
sector_score = market_data['sox_index'] / 100
print(f"  SOX: {market_data['sox_index']:+.1f}% → {sector_score:+.3f} (FLAT)")
print(f"  SECTOR TOTAL: {sector_score:+.3f}")

# 5. FUTURES
print(f"\n5️⃣ FUTURES:")
futures_score = market_data['nasdaq_futures'] / 100 * 0.5
print(f"  NASDAQ: {market_data['nasdaq_futures']:+.1f}% → {futures_score:+.3f}")
print(f"  FUTURES TOTAL: {futures_score:+.3f}")

# 6. MACRO
print(f"\n6️⃣ MACRO:")
vix_impact = 0.00
if market_data['vix'] < 18:
    vix_impact = +0.01
    print(f"  VIX {market_data['vix']:.1f} < 18: Calm (slight positive) {vix_impact:+.3f}")

dxy_impact = -market_data['dxy'] / 100 * 0.5
print(f"  DXY: {market_data['dxy']:+.1f}% → {dxy_impact:+.3f}")

yields_impact = 0.00
print(f"  Yields: Steady {yields_impact:+.3f}")

macro_score = vix_impact + dxy_impact + yields_impact
print(f"  MACRO TOTAL: {macro_score:+.3f}")

# 7. INSTITUTIONAL
print(f"\n7️⃣ INSTITUTIONAL:")
institutional_score = 0.00  # Average volume = no accumulation/distribution
print(f"  Average volume (no signal): {institutional_score:+.3f}")

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

# Market regime (neutral to slightly bullish)
market_regime = +0.005  # Very mild bullish
print(f"  Market Regime:  {market_regime:+.4f} (mild positive)")
total_score += market_regime
print(f"  {'─'*35}")
print(f"  {'FINAL SCORE':17s} {total_score:+.4f}")

# ========== DECISION ==========
print(f"\n{'='*80}")
print("🎯 SYSTEM DECISION LOGIC:")
print("="*80)

print(f"\nScore: {total_score:+.4f}")
print(f"Thresholds:")
print(f"  UP:      > +0.04")
print(f"  DOWN:    < -0.04")
print(f"  NEUTRAL: -0.04 to +0.04")

if total_score > 0.04:
    direction = "UP"
    color = "🟢"
    zone = "BULLISH ZONE"
elif total_score < -0.04:
    direction = "DOWN"
    color = "🔴"
    zone = "BEARISH ZONE"
else:
    direction = "NEUTRAL"
    color = "⚪"
    zone = "NEUTRAL DEADZONE"

print(f"\n{total_score:+.4f} is in the {zone}")
print(f"→ Direction: {color} {direction}")

# Confidence
confidence = 55 + abs(total_score) * 125
confidence = min(confidence, 95)

print(f"→ Confidence: {confidence:.1f}%")

# Trade decision
if direction == "NEUTRAL":
    trade_decision = "SKIP"
    reason = "Score in deadzone - no clear edge"
elif confidence >= 60:
    trade_decision = "TRADE"
    reason = f"Confidence {confidence:.1f}% ≥ 60%"
else:
    trade_decision = "SKIP"
    reason = f"Confidence {confidence:.1f}% < 60%"

print(f"→ Trade Decision: {trade_decision}")
print(f"→ Reason: {reason}")

# ========== PREDICTION ==========
print(f"\n{'='*80}")
print("🎯 FINAL PREDICTION:")
print("="*80)

print(f"\n{color} DIRECTION: {direction}")
print(f"📊 CONFIDENCE: {confidence:.1f}%")
print(f"📈 SCORE: {total_score:+.4f}")
print(f"💼 TRADE DECISION: {trade_decision}")

# Target
if direction == "UP":
    expected_move = abs(total_score) * 1.5
    target = stock_data['close'] * (1 + expected_move)
    print(f"\n💰 TARGET: ${target:.2f} (+{expected_move*100:.1f}%)")
elif direction == "DOWN":
    expected_move = abs(total_score) * 1.5
    target = stock_data['close'] * (1 - expected_move)
    print(f"\n💰 TARGET: ${target:.2f} (-{expected_move*100:.1f}%)")
else:
    print(f"\n💰 EXPECTED: ${stock_data['close']:.2f} ±0.5%")
    print(f"   Range: ${stock_data['close']*0.995:.2f} - ${stock_data['close']*1.005:.2f}")

# ========== REASONING ==========
print(f"\n{'='*80}")
print("💡 SIGNAL ANALYSIS:")
print("="*80)

bullish = []
bearish = []
neutral = []

for factor, score in weighted_scores.items():
    if score > 0.001:
        bullish.append(f"{factor} ({score:+.4f})")
    elif score < -0.001:
        bearish.append(f"{factor} ({score:+.4f})")
    else:
        neutral.append(f"{factor} (0.0000)")

print(f"\n🟢 BULLISH SIGNALS ({len(bullish)}):")
if bullish:
    for signal in bullish:
        print(f"  • {signal}")
else:
    print(f"  • None")

print(f"\n🔴 BEARISH SIGNALS ({len(bearish)}):")
if bearish:
    for signal in bearish:
        print(f"  • {signal}")
else:
    print(f"  • None")

print(f"\n⚪ NEUTRAL SIGNALS ({len(neutral)}):")
for signal in neutral[:3]:  # Show first 3
    print(f"  • {signal}")
if len(neutral) > 3:
    print(f"  • ... and {len(neutral)-3} more")

print(f"\n⚖️ THE BALANCE:")
print(f"  Bullish: {len(bullish)}")
print(f"  Bearish: {len(bearish)}")
print(f"  Neutral: {len(neutral)}")
print(f"  Net Score: {total_score:+.4f}")

# ========== COMPARISON TO OTHER SCENARIOS ==========
print(f"\n{'='*80}")
print("📊 COMPARISON TO OTHER TESTED SCENARIOS:")
print("="*80)

scenarios = [
    ("Clear Bearish", -0.078, "DOWN", 64.7, "TRADE"),
    ("Mixed Signals", +0.004, "NEUTRAL", 55.5, "SKIP"),
    ("High Volatility", -0.062, "DOWN", 52.8, "SKIP"),
    ("Strong Bullish", +0.110, "UP", 68.7, "TRADE"),
    ("Ultimate Test", -0.037, "NEUTRAL", 49.6, "SKIP"),
    ("Weak Bullish", total_score, direction, confidence, trade_decision),
]

print(f"\n{'Scenario':<20} {'Score':<8} {'Dir':<8} {'Conf%':<7} {'Decision':<10}")
print("─"*58)
for name, score, dir, conf, dec in scenarios:
    print(f"{name:<20} {score:+7.3f} {dir:<8} {conf:<7.1f} {dec:<10}")

# ========== CONCLUSION ==========
print(f"\n{'='*80}")
print("CONCLUSION:")
print("="*80)

print(f"""
AVGO Weak Bullish Analysis:
────────────────────────────────────────

{color} {direction} - {confidence:.1f}% Confidence

Score: {total_score:+.4f}

Why {direction}:
""")

if direction == "NEUTRAL" or confidence < 60:
    print(f"""⚪ WEAK SIGNALS DETECTED:
  • Score {total_score:+.4f} {'in' if abs(total_score) < 0.04 else 'near'} deadzone
  • Confidence {confidence:.1f}% < 60% threshold
  • {len(bullish)} bullish vs {len(bearish)} bearish vs {len(neutral)} neutral
  
📊 INDIVIDUAL SIGNALS:
  Positive: Options (+{options_score:.3f}), Technical (+{technical_score:.3f}), Futures (+{futures_score:.3f})
  Neutral: RSI, Volume, Institutional, Sector (flat)
  Negative: None significant

⚖️ SYSTEM REASONING:
  "Multiple mild positive signals, but NONE are strong"
  "No negative signals, but also no conviction"
  "Classic marginal setup - not worth the risk"

💡 SMART DECISION:
  {trade_decision}
  
  This is exactly when system should say "skip":
  • Not clearly bearish (no downside)
  • Not clearly bullish (weak upside)
  • No strong catalyst
  • Low conviction environment

🎯 EXPECTED BEHAVIOR:
  Most likely: Sideways/choppy (${stock_data['close']*0.995:.2f} - ${stock_data['close']*1.005:.2f})
  Could drift up on optimism or down on profit-taking
  No edge either way

✅ THIS IS PROFESSIONAL DISCIPLINE!
  Not every setup deserves a trade
  Preserving capital for better opportunities
  Waiting for confidence ≥60% and score outside deadzone

🔮 WHAT WOULD MAKE IT TRADEABLE:
  • Stronger news catalyst (currently +0.02, need +0.10+)
  • Volume surge (accumulation signal)
  • SOX sector strength (currently flat)
  • Options showing conviction (P/C 0.75 vs 0.95)
  • Score > +0.04 (currently {total_score:+.4f})
""")
elif direction == "UP":
    print(f"""🟢 MILD BULLISH SETUP:
  • Score {total_score:+.4f} slightly above +0.04
  • Confidence {confidence:.1f}%
  • {len(bullish)} positive signals
  
  Trade with CAUTION - borderline setup
""")

print("="*80)
