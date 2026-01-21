"""
Test Tom Hougaard Mode vs Standard Mode
========================================
Compare how Tom's conservative approach would filter recent predictions
"""

from tom_hougaard_mode import TomHougaardMode, compare_modes

def test_recent_predictions():
    """
    Test Tom Mode on our recent predictions:
    - AMD: 53.7% confidence (was WRONG)
    - AVGO: 55.6% confidence (was CORRECT)
    - ORCL: 54.3% confidence (was CORRECT)
    """
    
    tom_mode = TomHougaardMode()
    
    predictions = [
        {
            'symbol': 'AMD',
            'confidence': 53.7,
            'score': -0.087,
            'direction': 'DOWN',
            'entry_price': 150.00,
            'target': 145.00,
            'stop_loss': 152.00,
            'stop_loss_percent': 1.33,
            'actual_result': 'WRONG (went UP)',
            'components': {
                'futures': {'score': 0.05, 'weight': 0.15},
                'options': {'score': -0.03, 'weight': 0.11},
                'technical': {'score': -0.02, 'weight': 0.08},
                'sector': {'score': -0.04, 'weight': 0.10},
                'news': {'score': 0.02, 'weight': 0.08}
            }
        },
        {
            'symbol': 'AVGO',
            'confidence': 55.6,
            'score': 0.042,
            'direction': 'UP',
            'entry_price': 175.00,
            'target': 180.00,
            'stop_loss': 173.00,
            'stop_loss_percent': 1.14,
            'actual_result': 'CORRECT (went UP)',
            'components': {
                'futures': {'score': 0.06, 'weight': 0.15},
                'options': {'score': 0.04, 'weight': 0.11},
                'technical': {'score': 0.03, 'weight': 0.08},
                'news': {'score': 0.05, 'weight': 0.11},
                'institutional': {'score': 0.02, 'weight': 0.10}
            }
        },
        {
            'symbol': 'ORCL',
            'confidence': 54.3,
            'score': 0.038,
            'direction': 'UP',
            'entry_price': 130.00,
            'target': 134.00,
            'stop_loss': 128.50,
            'stop_loss_percent': 1.15,
            'actual_result': 'CORRECT (went UP)',
            'components': {
                'futures': {'score': 0.05, 'weight': 0.16},
                'institutional': {'score': 0.04, 'weight': 0.16},
                'technical': {'score': 0.02, 'weight': 0.08},
                'options': {'score': 0.03, 'weight': 0.11},
                'news': {'score': 0.06, 'weight': 0.14}
            }
        }
    ]
    
    print("=" * 80)
    print("🎯 TOM HOUGAARD MODE: FILTERING RECENT PREDICTIONS")
    print("=" * 80)
    print("\nTom's Rules:")
    print("✅ Min 55% confidence (vs our 50%)")
    print("✅ 1% risk per trade (vs our 2%)")
    print("✅ R:R min 2.5:1 (vs our 1.67:1)")
    print("✅ London/NY session only")
    print("✅ Price action focus")
    print("\n" + "=" * 80)
    
    account_balance = 10000
    tom_approved = 0
    standard_correct = 0
    tom_correct = 0
    
    for pred in predictions:
        print(f"\n📊 {pred['symbol']} - Standard Mode Prediction")
        print("-" * 80)
        print(f"   Confidence: {pred['confidence']}%")
        print(f"   Direction: {pred['direction']}")
        print(f"   Score: {pred['score']:.4f}")
        print(f"   Entry: ${pred['entry_price']:.2f}")
        print(f"   Target: ${pred['target']:.2f}")
        print(f"   Stop: ${pred['stop_loss']:.2f}")
        print(f"   Result: {pred['actual_result']}")
        
        # Check if standard mode was correct
        if 'CORRECT' in pred['actual_result']:
            standard_correct += 1
        
        # Apply Tom's filters
        tom_result = tom_mode.filter_signals(pred)
        
        print(f"\n🎯 Tom Hougaard Mode Decision:")
        if tom_result['tom_approved']:
            tom_approved += 1
            print(f"   ✅ APPROVED")
            
            # Generate trade plan
            trade_plan = tom_mode.generate_trade_plan(pred, account_balance)
            print(f"   Risk: ${trade_plan['risk_amount']:.2f} ({trade_plan['risk_percent']}%)")
            print(f"   Position: ${trade_plan['position_size']:.2f}")
            print(f"   Session: {trade_plan['session']}")
            
            # Check if would have been correct
            if 'CORRECT' in pred['actual_result']:
                tom_correct += 1
                print(f"   📈 Would have been PROFITABLE")
            else:
                print(f"   📉 Would have lost (but only 1% risk)")
        else:
            print(f"   ❌ REJECTED")
            print(f"   Reason: {tom_result['reason']}")
            print(f"   💡 Tom says: 'Wait for better setup'")
        
        # Show price action mode
        simplified = tom_mode.simplify_prediction(pred)
        print(f"\n💡 Tom's Price Action Only:")
        print(f"   Score: {simplified['score']:.4f}")
        print(f"   Confidence: {simplified['confidence']}%")
        print(f"   Direction: {simplified['direction']}")
        print(f"   (Using only: futures, options, technical, S/R)")
        
        print("\n" + "=" * 80)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE COMPARISON")
    print("=" * 80)
    
    standard_win_rate = (standard_correct / len(predictions)) * 100
    print(f"\n🔵 STANDARD MODE:")
    print(f"   Trades Taken: {len(predictions)}/3")
    print(f"   Correct: {standard_correct}")
    print(f"   Win Rate: {standard_win_rate:.1f}%")
    print(f"   Risk Per Trade: 2%")
    
    if tom_approved > 0:
        tom_win_rate = (tom_correct / tom_approved) * 100
        print(f"\n🎯 TOM HOUGAARD MODE:")
        print(f"   Trades Taken: {tom_approved}/3")
        print(f"   Correct: {tom_correct}")
        print(f"   Win Rate: {tom_win_rate:.1f}%")
        print(f"   Risk Per Trade: 1%")
        
        # Calculate ROI
        standard_roi = (standard_correct * 3.34) - ((len(predictions) - standard_correct) * 2)
        tom_roi = (tom_correct * 2.5) - ((tom_approved - tom_correct) * 1) if tom_approved > 0 else 0
        
        print(f"\n💰 ESTIMATED ROI (simplified):")
        print(f"   Standard Mode: {standard_roi:.1f}%")
        print(f"   Tom Mode: {tom_roi:.1f}%")
    else:
        print(f"\n🎯 TOM HOUGAARD MODE:")
        print(f"   Trades Taken: 0/3")
        print(f"   Reason: All predictions rejected by Tom's strict filters")
        print(f"   💡 Tom would say: 'No edge = No trade'")
    
    print("\n" + "=" * 80)
    print("🎓 KEY LESSONS:")
    print("=" * 80)
    print()
    print("1. 🎯 Tom's stricter filters (55% min confidence) would reject AMD")
    print("   → This would have AVOIDED the losing trade!")
    print()
    print("2. 💰 Lower risk (1% vs 2%) means smaller losses when wrong")
    print("   → More sustainable for long-term trading")
    print()
    print("3. 🔍 Fewer trades = Higher quality setups")
    print("   → Tom: 'Wait for the fat pitch'")
    print()
    print("4. ⚖️ Trade-off: Fewer opportunities vs Better risk management")
    print("   → Standard: More trades, 66.7% win rate")
    print("   → Tom: Fewer trades, higher win rate potential")
    print()
    print("=" * 80)
    print()
    print("💡 RECOMMENDATION:")
    print("   Use TOM MODE when:")
    print("   ✅ Learning the system (lower risk)")
    print("   ✅ Small account (<$5k)")
    print("   ✅ Risk-averse personality")
    print("   ✅ Want higher quality setups only")
    print()
    print("   Use STANDARD MODE when:")
    print("   ✅ Confident in system (after 30+ trades)")
    print("   ✅ Larger account (>$10k)")
    print("   ✅ Want more trading opportunities")
    print("   ✅ Comfortable with 50-55% confidence trades")
    print()
    print("=" * 80)


if __name__ == "__main__":
    test_recent_predictions()
