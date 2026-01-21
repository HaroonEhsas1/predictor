# API Key Requirements for Institutional Data Sources

To access premium institutional-level data sources, you'll need API keys from the following providers:

## Essential API Keys (High Priority)

### 1. Alpha Vantage (FREE tier available)
- **Purpose**: Options flow data, intraday data, technical indicators
- **Sign up**: https://www.alphavantage.co/support/#api-key
- **Environment Variable**: `ALPHA_VANTAGE_API_KEY`
- **Free Tier**: 5 API requests per minute, 500 requests per day

### 2. Polygon.io (Paid - High Value)
- **Purpose**: Level 2 data, real-time market data, options flow
- **Sign up**: https://polygon.io/pricing
- **Environment Variable**: `POLYGON_API_KEY`
- **Cost**: $99/month for real-time data access
- **Value**: Access to institutional-grade market microstructure data

### 3. Quandl/Nasdaq Data (Premium)
- **Purpose**: Financial and economic data, institutional positioning
- **Sign up**: https://data.nasdaq.com/
- **Environment Variable**: `QUANDL_API_KEY`
- **Cost**: Varies by dataset, some free datasets available

## Advanced API Keys (Lower Priority)

### 4. IEX Cloud
- **Purpose**: Market data, earnings, insider transactions
- **Sign up**: https://iexcloud.io/pricing/
- **Environment Variable**: `IEX_CLOUD_API_KEY`
- **Free Tier**: Available with limitations

### 5. Benzinga
- **Purpose**: News sentiment, insider trading data
- **Sign up**: https://benzinga.com/apis/
- **Environment Variable**: `BENZINGA_API_KEY`
- **Cost**: Premium service

### 6. CBOE (Chicago Board Options Exchange)
- **Purpose**: Options data, volatility indices
- **Sign up**: https://www.cboe.com/market_data/
- **Environment Variable**: `CBOE_API_KEY`
- **Cost**: Premium institutional data

### 7. TD Ameritrade API
- **Purpose**: Real-time quotes, options chains, Level 2 data
- **Sign up**: https://developer.tdameritrade.com/
- **Environment Variable**: `TD_AMERITRADE_API_KEY`
- **Cost**: Free with TD Ameritrade account

## How to Set API Keys

Add these to your Replit environment:

```bash
# In Replit Secrets (recommended)
ALPHA_VANTAGE_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
QUANDL_API_KEY=your_key_here
IEX_CLOUD_API_KEY=your_key_here
BENZINGA_API_KEY=your_key_here
CBOE_API_KEY=your_key_here
TD_AMERITRADE_API_KEY=your_key_here
```

## What Each API Provides

### Alpha Vantage
- Real-time and historical stock prices
- Technical indicators (RSI, MACD, etc.)
- Options data (limited)
- Forex and crypto data

### Polygon.io
- **LEVEL 2 ORDER BOOK DATA** (institutional support/resistance levels)
- Real-time trades and quotes
- Options flow and unusual activity
- Market microstructure data
- Aggregated trade data

### Quandl
- COT (Commitment of Traders) reports
- Economic indicators
- Alternative datasets
- Institutional positioning data

### IEX Cloud
- Real-time market data
- Corporate earnings and fundamentals
- Insider transaction data
- Social sentiment data

## Priority Recommendation

**Start with Alpha Vantage (free)** and **Polygon.io (paid)** for maximum impact:

1. **Alpha Vantage**: Free access to basic institutional indicators
2. **Polygon.io**: Premium access to Level 2 data and real institutional flow

These two APIs will unlock 80% of the institutional intelligence capabilities in the system.

## Current Fallback Strategy

Without API keys, the system currently uses:
- Yahoo Finance as primary data source
- Proxy calculations for institutional activity
- Volume/price analysis for dark pool detection
- Options chain analysis for gamma exposure

With proper API keys, you'll access:
- Real Level 2 order book data
- Actual options flow and unusual activity
- Professional-grade market microstructure analysis
- Institutional positioning reports