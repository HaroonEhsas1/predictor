# Next-Day Prediction Engine

Professional institutional-grade prediction system for overnight gap analysis with comprehensive safety controls.

## Overview

The Next-Day Prediction Engine implements institutional best practices for overnight gap prediction including:

- ✅ **Purged time-series cross-validation** to prevent data leakage
- ✅ **Isotonic probability calibration** for reliable confidence scores  
- ✅ **Ensemble modeling** with adaptive weights
- ✅ **Strict confidence gating** (80% threshold) and consensus requirements
- ✅ **Comprehensive risk management** with position sizing controls
- ✅ **Feature flag controls** with dry-run enforcement by default

## Architecture

```
engines/nextday/
├── config.py          # Configuration and safety controls
├── data_ingest.py      # Professional data collection with validation
├── features.py         # Institutional-grade feature engineering  
├── models.py           # ML ensemble with proper validation
├── gate.py             # Gating system and risk management
├── predict.py          # Main prediction orchestrator
├── tests/              # Comprehensive unit tests
└── README.md          # This file
```

## Data Sources

### Core Market Data
- **AMD**: Primary asset for prediction
- **ES/NQ Futures**: Overnight market sentiment
- **VIX**: Volatility regime detection
- **SOXX**: Semiconductor sector context
- **NVDA**: Correlation analysis

### Engineered Features (15 total)
1. **Overnight futures delta** (volatility-weighted)
2. **Options GEX exposure** (simulated from volume patterns)
3. **Rolling volatility** (5/10/20 day windows)
4. **Overnight news sentiment** (price action proxy)
5. **Liquidity heatmap distance**
6. **Block trade imbalance**
7. **Dark pool ratio estimates**
8. **VIX regime change indicator**
9. **SOXX relative strength**
10. **NVDA correlation factor**
11. **Volume anomaly score**
12. **Momentum reversal signal**
13. **Cross-asset stress index**

## Model Ensemble

### Algorithms
- **Gradient Boosting**: Primary model for non-linear patterns
- **Random Forest**: Robust ensemble learner
- **Ridge Regression**: Linear baseline with regularization

### Validation
- **Time Series CV**: 5-fold with 2-day purging to prevent leakage
- **Out-of-sample testing**: Walk-forward validation
- **Probability calibration**: Isotonic regression for reliable confidence
- **Ensemble weighting**: Adaptive based on recent performance

## Safety Controls

### Gating Requirements (ALL must pass)
1. **Confidence ≥ 80%** (calibrated probability)
2. **Ensemble consensus ≥ 80%** (directional agreement)  
3. **Minimum gap magnitude ≥ 0.5%** (institutional relevance)
4. **Risk limits** (position size, daily exposure)
5. **Feature flag enabled** (`nextday.enabled: true`)

### Risk Management
- **Maximum position size**: 2% per trade
- **Daily exposure limit**: 6% aggregate
- **Stop loss**: 3% automatic
- **Dry run enforcement**: No live trades by default

## Usage

### Basic Prediction
```python
from engines.nextday import NextDayPredictor

# Initialize predictor
predictor = NextDayPredictor()

# Generate prediction
result = predictor.generate_prediction()

print(f"Direction: {result['direction']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Trade Signal: {result['trade_signal']}")
```

### Command Line Interface
```bash
# Generate prediction (dry run)
python -m engines.nextday.predict

# Train new models  
python -m engines.nextday.predict --train

# Use specific model version
python -m engines.nextday.predict --model-version 20250819
```

### Configuration
```python
from engines.nextday import CONFIG, update_config

# Enable feature (disabled by default)
update_config({'enabled': True})

# Adjust thresholds (institutional defaults)
update_config({
    'min_confidence': 0.85,      # 85% confidence required
    'min_ensemble_consensus': 0.80,  # 80% consensus required
    'max_position_size': 0.015   # 1.5% max position
})
```

## Installation & Setup

### 1. Enable Feature Flag
```python
# In your configuration
CONFIG.enabled = True    # Enable next-day engine
CONFIG.dry_run = True    # Keep dry run for safety
```

### 2. Train Initial Models
```python
from engines.nextday import NextDayPredictor

predictor = NextDayPredictor()
results = predictor.train_models(lookback_days=252)  # 1 year
print(f"Training completed: {results['n_samples']} samples")
```

### 3. Validate Setup
```python
# Run unit tests
python engines/nextday/tests/test_nextday.py

# Check status
status = predictor.get_status()
print(f"Models loaded: {status['models_loaded']}")
print(f"Confidence threshold: {status['confidence_threshold']:.0%}")
```

## Live Trading Setup

⚠️ **IMPORTANT**: Live trading requires explicit enablement and additional validation.

### Prerequisites for Live Mode
1. ✅ **Models trained** with >75% out-of-sample accuracy
2. ✅ **Risk management** configured and tested
3. ✅ **Position sizing** validated with realistic slippage
4. ✅ **Stop loss** mechanisms in place
5. ✅ **Monitoring** and alerting configured

### Enable Live Trading
```python
# ONLY after thorough validation
CONFIG.dry_run = False           # Disable dry run
CONFIG.enabled = True            # Enable feature
CONFIG.min_confidence = 0.85     # High confidence required
```

### Live Trading Checklist
- [ ] Backtest results validated over 6+ months OOS
- [ ] Risk limits tested with realistic position sizes
- [ ] Stop loss and exit strategies implemented
- [ ] Real-time monitoring and alerting configured
- [ ] Rollback procedures documented and tested
- [ ] Regulatory compliance verified

## Monitoring & Maintenance

### Key Metrics to Monitor
- **Prediction accuracy** (rolling 30-day)
- **Confidence calibration** (predicted vs actual)
- **Gating statistics** (approval rates, common failures)
- **Risk utilization** (position sizes, daily exposure)
- **Model drift** (feature distributions, prediction patterns)

### Retraining Schedule
- **Weekly**: Update ensemble weights based on recent performance
- **Monthly**: Retrain models with latest data
- **Quarterly**: Full validation and hyperparameter optimization

### Alerts
- Model accuracy drops below 65%
- Confidence calibration drift > 10%
- Risk limits breached
- Data quality issues detected
- Feature distributions change significantly

## API Reference

### NextDayPredictor

Main prediction interface.

```python
predictor = NextDayPredictor(model_version='20250819')

# Generate prediction
result = predictor.generate_prediction(lookback_days=60)

# Train models
training_results = predictor.train_models(lookback_days=252)

# Check status
status = predictor.get_status()
```

### Prediction Result Format
```python
{
    'direction': 'UP|DOWN|SKIP',
    'confidence': 0.85,                    # Calibrated probability
    'trade_signal': 'UP|DOWN|NO_TRADE',    # Post-gating signal
    'predicted_gap_pct': 0.015,           # Expected gap percentage
    'expected_open': 168.50,              # Expected opening price
    'position_size': 0.018,               # Recommended position size
    'gate_reasons': [...],                # Reasons for gating decisions
    'passed_gates': [...],                # Gates that passed
    'model_predictions': {...},           # Individual model outputs
    'ensemble_weights': {...},            # Current ensemble weights
    'dry_run_mode': True,                 # Safety flag
    'prediction_timestamp': '...'         # ISO timestamp
}
```

## Troubleshooting

### Common Issues

**"No trained models available"**
- Run model training first: `predictor.train_models()`
- Check if model files exist in `models/nextday/`

**"Feature flag disabled"**  
- Enable feature: `CONFIG.enabled = True`
- Check configuration: `predictor.get_status()`

**"Insufficient training data"**
- Ensure 60+ days of market data available
- Check data quality validation logs

**"Low confidence predictions"**
- Normal during uncertain market conditions
- Consider retraining with recent data
- Review feature engineering for regime changes

## Support

For technical issues or questions about institutional implementation:

1. Check unit tests: `python engines/nextday/tests/test_nextday.py`
2. Review logs for detailed error information
3. Validate configuration with `predictor.get_status()`
4. Ensure all prerequisites met for intended usage mode

---

⚠️ **Risk Disclosure**: This system is designed for institutional use with proper risk management. Past performance does not guarantee future results. Always use appropriate position sizing and risk controls.