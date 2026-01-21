# AI-Powered Stock Trading Intelligence Platform

## Overview
This project is an advanced AI-powered stock trading intelligence platform designed to provide sophisticated market gap prediction and multi-dimensional predictive analytics. Its primary purpose is to deliver highly accurate, unbiased, and confidence-gated investment signals for strategic decision-making, focusing on capturing small directional edges and significant profit movements. The platform integrates institutional-grade data and advanced machine learning techniques to achieve high-accuracy predictions and aims to offer a competitive advantage in dynamic market conditions.

## User Preferences
- Focus on accuracy over speed
- Prefer comprehensive analysis over simplified outputs
- Wants fully predictive (not reactive) systems
- Values academic research-backed methodologies
- Prefers detailed signal explanations

## System Architecture
The platform is built around a robust, multi-engine architecture focusing on institutional-grade market intelligence and precise predictive analytics.

### Core Architectural Principles
- **Bias Elimination**: Systematically designed to remove directional biases.
- **Confidence Gating**: All prediction engines incorporate dynamic confidence thresholds (e.g., 55% to 85%) to filter signals and manage risk.
- **Ensemble ML Models**: Utilizes multiple machine learning algorithms (Gradient Boosting, Random Forest, LSTM, Ridge Regression) per prediction direction.
- **Modular Design**: Engines operate independently with clear interfaces.
- **Professional Controls**: Incorporates institutional-grade features like purged time-series cross-validation and isotonic probability calibration.
- **Adaptive Learning System**: Eliminates hardcoded values by replacing them with market-learned values and continuously recalibrates thresholds based on prediction performance.
- **Predictive Architecture Overhaul**: Prioritizes forward-looking data such as futures and options flow analysis, significantly reducing reliance on lagging indicators.

### Key Engines and Modules
- **Enhanced Ultra Accurate Gap Predictor** (CORE): A 6-layer institutional architecture with pre-close focused analysis, action-oriented BUY/SELL/HOLD signals, and smart change detection.
- **Precision Profit Engine**: Specializes in predicting precise $0.30 profit movements using 56 elite data sources, 42+ precision indicators, and multiple ML algorithms.
- **Institutional Market Intelligence**: Accesses and processes high-value market data such as Level 2 order book analysis, dark pool data, options flow, and insider trading patterns.
- **StackingMetaLearner**: Advanced ensemble technique combining predictions from multiple base models, integrated into both intraday and next-day engines with a 70/30 blending strategy.
- **Multi-Source Data Aggregator**: Expands data collection from numerous free sources with intelligent fallback chains, covering price, fundamentals, sentiment, macro, and institutional data.
- **Enhanced Confidence Gating**: Implements multi-layer probability calibration and Bayesian Model Averaging with dynamic thresholds based on market regime.
- **Institutional Insights Engine**: Detects dark pool activity, block trades, smart money index, options flow, insider trading, and ETF correlation.

### Technology Stack
-   **Core Language**: Python
-   **Data Acquisition**: yfinance
-   **Data Analysis**: NumPy, Pandas
-   **Machine Learning**: Scikit-learn, and potentially TensorFlow/Keras for LSTM
-   **API Development**: Flask

## External Dependencies
The platform integrates with various external data providers and services for comprehensive market intelligence. API keys are required for premium access to these services; otherwise, the system may rely on sophisticated proxy calculations.

### Core Data Sources
-   **Alpha Vantage**: Options flow and technical indicators.
-   **Polygon.io**: Level 2 data and real-time market microstructure.
-   **Quandl**: COT reports and institutional positioning data.
-   **IEX Cloud**: Insider transactions and earnings intelligence.
-   **Benzinga**: News sentiment and insider activity alerts.
-   **CBOE**: Professional options data and volatility indices.
-   **TD Ameritrade**: Real-time quotes and Level 2 access.
-   **StockData.org**: Unlimited free historical data, real-time quotes, OHLCV, technical indicators, fundamentals.
-   **TwelveData**: Real-time and historical data, 50+ technical indicators.
-   **SEC Edgar**: Company filings for insider trading and other disclosures.
-   **Reddit (via PRAW)**: Social sentiment analysis.

### Premium Data Sources
-   **Financial Modeling Prep (FMP)**: Institutional-grade fundamental data, analyst estimates, earnings, financial ratios, ownership, and insider trading.
-   **MarketAux**: Advanced news sentiment with entity extraction, real-time sentiment analysis, and trending stock detection.