# After Close Engine

A modular, independent engine for generating pre-market gap predictions using overnight data. This engine operates separately from the main AMD prediction system and provides predictions through JSON output files.

## Overview

The After Close Engine collects overnight market data (futures, options flow, news sentiment, global indices) and generates directional predictions for the next trading day's market open. It's designed to be:

- **Independent**: Never modifies main application code
- **Modular**: Clean separation of concerns with mockable data sources  
- **Safe**: Includes dry-run mode and comprehensive testing
- **Production-ready**: Atomic file writes, proper logging, health checks

## Quick Start

1. **Install dependencies:**
   ```bash
   cd engines/after_close_engine
   pip install -r requirements.txt
   ```

2. **Test with dry run:**
   ```bash
   python engine.py predict --mode dry-run
   ```

3. **Generate prediction:**
   ```bash
   python engine.py predict
   ```

4. **Start API server (optional):**
   ```bash
   python engine.py serve
   ```

## CLI Commands

- `python engine.py collect` - Run data collection once
- `python engine.py predict` - Generate prediction and write JSON
- `python engine.py predict --mode dry-run` - Test prediction without writing files
- `python engine.py predict --auto-fit` - Enable auto-training if models missing
- `python engine.py serve` - Start Flask API server

## Configuration

Create `.env` file or set environment variables:

```bash
# Core settings
AFTER_CLOSE_ENABLED=true
CONFIDENCE_THRESHOLD=0.70
PREDICTION_PATH=/data/predictions/after_close
LOG_PATH=/logs/after_close

# Development settings
AUTO_FIT_ON_DEV=false
DEBUG_MODE=false
TIMEZONE=US/Eastern

# API settings (optional)
SERVE_PORT=5001
SERVE_HOST=0.0.0.0
```

## Data Sources

The engine fetches data from multiple sources (easily mockable for development):

1. **Futures**: ES/NQ overnight moves
2. **Options Flow**: Call/put flow summaries  
3. **News Sentiment**: Headline analysis and sentiment scores
4. **Global Indices**: Overnight international market moves
5. **Intraday Snapshot**: Main system data from `/data/engine_snapshot/latest.json`

## Integration with Main App

The main application can read predictions via:

1. **File-based**: Read `/data/predictions/after_close/latest.json`
2. **HTTP API**: GET `http://localhost:5001/after_close/prediction` (if serve mode enabled)

**Example prediction JSON structure:**
```json
{
  "timestamp": "2025-08-19T21:30:00Z",
  "symbol": "AMD", 
  "direction": "DOWN",
  "expected_open": 168.45,
  "confidence": 0.72,
  "features": {
    "overnight_futures_pct": -0.8,
    "net_options_flow": 0.35,
    "news_sentiment_score": -0.2,
    "global_index_impact_score": -0.1
  },
  "model_version": "v1.0"
}
```

## Model Architecture

1. **Feature Engineering**: 6 normalized features using StandardScaler
2. **LightGBM**: Primary tabular model for overnight patterns  
3. **LSTM**: Sequential model using last 4 overnight snapshots (if available)
4. **Ensemble**: Weighted combination of both models

## Safety & Production Notes

- **Non-reactive**: Uses only pre-market data, never live tick data
- **Atomic writes**: Predictions written safely with temp files
- **Gated confidence**: Outputs SKIP if confidence < threshold
- **No main app changes**: Completely isolated operation
- **Auto-fit gating**: Model training only when explicitly enabled

## Testing

Run comprehensive tests:
```bash
cd tests
python -m pytest test_fetchers.py -v
python -m pytest test_predict_cli.py -v
```

## Troubleshooting

1. **Missing models**: Run with `--auto-fit` flag once
2. **Data collection fails**: Check network connectivity and API limits  
3. **Low confidence**: Adjust CONFIDENCE_THRESHOLD in environment
4. **Permission errors**: Ensure write access to prediction and log directories

## Production Deployment

1. Set `AFTER_CLOSE_ENABLED=true`
2. Run as separate process/worker (not embedded in web server)
3. Schedule collection after market close (4:30 PM ET)
4. Generate predictions before market open (9:00 AM ET)
5. Monitor logs in `/logs/after_close/`

## API Endpoints (Serve Mode)

- `GET /after_close/prediction` - Latest prediction JSON
- `GET /health` - Health check status
- `GET /status` - Engine status and last run info