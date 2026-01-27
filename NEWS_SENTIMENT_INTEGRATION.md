# Real-Time News Sentiment Integration - Premarket System

## Overview
The premarket multi-stock prediction system now integrates **real-time news sentiment** with ML-based predictive models for each stock (AMD, NVDA, META, AVGO, SNOW, PLTR).

## How It Works

### 1. **News Sentiment Fetching (Priority 1)**
- **Source**: Multiple APIs via `RealTimeNewsSentiment` class
  - Finnhub (free tier for recent news)
  - MarketAux (alternative API)
  - Alpha Vantage (economic data)
  
- **Frequency**: Real-time, fetched at prediction time
- **Lookback**: 24 hours of recent news for each stock

### 2. **ML Model Blending**
Each stock has a trained news reaction model:
- `models/news_model_AMD.joblib`
- `models/news_model_NVDA.joblib`
- `models/news_model_META.joblib`
- `models/news_model_AVGO.joblib`
- `models/news_model_SNOW.joblib`
- `models/news_model_PLTR.joblib`

**Blending Formula:**
```
Blended Sentiment = (Raw Keyword Sentiment × 0.4) + (ML Model Sentiment × 0.6)
```

The models are Pipeline objects that:
- Extract features from news headlines
- Classify sentiment as: UP, DOWN, or NEUTRAL
- Convert to scores: UP=+1.0, DOWN=-1.0, NEUTRAL=0.0
- Average across recent articles

### 3. **Confidence Boost Logic**
Based on sentiment magnitude:

| Sentiment Range | Confidence Boost |
|---|---|
| ±0.5 to ±1.0 | +10% |
| ±0.3 to ±0.5 | +5% |
| ±0.0 to ±0.3 | 0% |

Boost is only applied if sentiment magnitude exceeds threshold.

## Integration Points

### In `premarket_multi_stock.py`:

1. **Data Fetching** (Lines ~450-460):
```python
news_result = get_news_sentiment_with_ml(symbol)
blended_sentiment = news_result.get('blended_sentiment', 0.0)
article_count = news_result.get('articles_count', 0)
model_used = news_result.get('model_used', False)
```

2. **Predictor Data Enhancement** (Lines ~464-474):
```python
predictor_data['news_sentiment'] = blended_sentiment
predictor_data['news_articles_count'] = article_count
predictor_data['news_confidence_boost'] = confidence_boost
```

3. **Result Reporting** (Lines ~636-638):
News sentiment is included in trading summary output

## Current Status

✅ **Implemented:**
- Real-time news fetching for all 6 stocks
- ML model loading and inference (60% weight)
- Raw keyword sentiment analysis (40% weight)
- Confidence boost calculation
- Results reporting in trading summary

⚠️ **API Limitations:**
- Finnhub free tier limits requests to 60/minute
- MarketAux requires separate API key
- During market hours, may hit rate limits
- See `api_key_requirements.md` for setup

## Usage

### Run premarket predictions with integrated news:
```bash
python premarket_multi_stock.py
```

### View news details in output:
```
AMD:
   Direction: DOWN
   Confidence: 93.8%
   News Sentiment: +0.15 (3 articles)  # ← Shows sentiment
   News Confidence Boost: +5%           # ← Shows boost
```

## Next Steps

1. **API Optimization** (Priority 2):
   - Cache news between runs
   - Rate-limit management
   - Fallback APIs for redundancy

2. **ML Enhancement** (Priority 2):
   - Retrain models with more recent data
   - Add sector-specific sentiment models
   - Incorporate social media signals

3. **Integration Expansion**:
   - Pass news_confidence_boost to predictor.predict()
   - Use news_sentiment as input feature
   - Track news vs price correlation

## Testing

Test news integration:
```bash
python test_news_integration.py
```

Shows:
- Model loading for each stock
- Sample sentiment predictions
- Success/failure of news fetching

## Files Modified

1. `premarket_multi_stock.py` - Added news sentiment fetching and integration
2. `intraday_1hour_predictor.py` - Contains RealTimeNewsSentiment class (already had it)
3. `test_news_integration.py` - New test file

## Error Handling

If news fetching fails:
- System falls back to `news_sentiment = 0.0`
- No boost applied
- Predictions continue normally
- Warning logged to `premarket_predictions.log`

Example failure modes:
- API rate limit exceeded
- No recent articles found
- Network connectivity issues
- Invalid API keys

All handled gracefully with fallback logic.
