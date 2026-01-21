#!/usr/bin/env python3
"""Deep verification of calculation accuracy"""

# The values from the logs
news = 0.07
futures = 0.59
crypto = 0.25
sector = -0.70

print('🔍 DEEP VERIFICATION - STEP BY STEP')
print('=' * 80)
print('\n📊 RAW VALUES FROM LOGS:')
print(f'   News:    {news:+.2f}')
print(f'   Futures: {futures:+.2f}')
print(f'   Crypto:  {crypto:+.2f}')
print(f'   Sector:  {sector:+.2f}')

print('\n🔢 CALCULATION (from codebase line 9682):')
print('   Formula: (news × 0.50) + (futures × 0.35) + (crypto × 0.10) + (sector × 0.05)')
print()
print(f'   News:    {news:+.2f} × 0.50 = {news * 0.50:+.4f}')
print(f'   Futures: {futures:+.2f} × 0.35 = {futures * 0.35:+.4f}')
print(f'   Crypto:  {crypto:+.2f} × 0.10 = {crypto * 0.10:+.4f}')
print(f'   Sector:  {sector:+.2f} × 0.05 = {sector * 0.05:+.4f}')
print('   ' + '-' * 50)

overall = (news * 0.50) + (futures * 0.35) + (crypto * 0.10) + (sector * 0.05)
print(f'   TOTAL:   {overall:+.4f}')

print('\n📏 THRESHOLD CHECK (from codebase line 9690):')
data_quality = 3  # All 3 sources have data
quality_factor = min(data_quality / 3.0, 1.0)
threshold = 0.08 + (0.04 * (1.0 - quality_factor))
print(f'   Data quality: {data_quality}/3 sources')
print(f'   Quality factor: {quality_factor:.2f}')
print(f'   Threshold: ±{threshold:.3f}')

print('\n🎯 SIGNAL DETERMINATION (from codebase lines 9692-9712):')
if overall > threshold:
    direction = 'UP / BULLISH'
    signal = 'BUY'
    base_conf = 58
    sentiment_boost = min(overall * 30, 30)
    quality_boost = quality_factor * 5
    confidence = min(base_conf + sentiment_boost + quality_boost, 88.0)
elif overall < -threshold:
    direction = 'DOWN / BEARISH'
    signal = 'SELL'
    base_conf = 58
    sentiment_boost = min(abs(overall) * 30, 30)
    quality_boost = quality_factor * 5
    confidence = min(base_conf + sentiment_boost + quality_boost, 88.0)
else:
    direction = 'NEUTRAL'
    signal = 'HOLD'
    neutrality_strength = 1.0 - (abs(overall) / threshold)
    base_neutral = 40 + (data_quality * 3)
    confidence = min(base_neutral + (neutrality_strength * 10), 52)

print(f'   Overall: {overall:+.4f}')
print(f'   Threshold: ±{threshold:.3f}')
print(f'   {overall:+.4f} > {threshold:.3f}? {overall > threshold}')
print()
print('=' * 80)
print(f'✅ FINAL SIGNAL: {signal} ({direction})')
print(f'✅ CONFIDENCE: {confidence:.1f}%')
print('=' * 80)

# Double check with absolute precision
print('\n🔬 ABSOLUTE PRECISION CHECK:')
print(f'   0.07 × 0.50 = {0.07 * 0.50}')
print(f'   0.59 × 0.35 = {0.59 * 0.35}')
print(f'   0.25 × 0.10 = {0.25 * 0.10}')
print(f'   -0.70 × 0.05 = {-0.70 * 0.05}')
print(f'   SUM = {0.07*0.50 + 0.59*0.35 + 0.25*0.10 + (-0.70)*0.05}')
print(f'   Is {0.07*0.50 + 0.59*0.35 + 0.25*0.10 + (-0.70)*0.05} > 0.08? {(0.07*0.50 + 0.59*0.35 + 0.25*0.10 + (-0.70)*0.05) > 0.08}')
