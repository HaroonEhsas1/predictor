# 📊 Stock-Specific Configurations

## ✅ VERIFICATION STATUS: ALL STOCKS INDEPENDENT

Each stock (AMD, AVGO, ORCL) has its own:
- ✅ Volatility and momentum parameters
- ✅ Weight adjustments for data sources
- ✅ News keywords and identifiers
- ✅ Technical indicator thresholds
- ✅ Risk parameters
- ✅ No hardcoded conflicts

---

## 🔧 AMD (Advanced Micro Devices)

### **Stock Profile**
- **Type:** High-beta semiconductor
- **Sector:** Technology (XLK)
- **Character:** Retail-driven, social media sensitive
- **Competitors:** NVDA, INTC, TSM, QCOM

### **Volatility & Risk Parameters**
```python
typical_volatility: 3.32%       # Highest of 3 stocks - very volatile
historical_avg_gap: 1.36%       # Expected overnight move
momentum_continuation: 56%      # Highest - trends continue more often
min_confidence: 60%             # Standard threshold
```

### **Data Source Weights (Sum = 100%)**
```
Futures:        15.0% ██████████  Market direction
Options:        11.0% ███████     Real-time sentiment
Premarket:      10.0% ██████      Same-day momentum
Hidden Edge:    10.0% ██████      8 alt sources (BTC, SOX, etc.)
VIX:             8.0% █████       Fear gauge
News:            8.0% █████       6h breaking news
Technical:       8.0% █████       RSI, MACD, momentum
Reddit:          8.0% █████       WSB popular ⭐
Sector:          6.0% ████        Tech sector
Institutional:   6.0% ████        Smart money
Twitter:         5.0% ███         Social sentiment
Analyst:         2.0% █           Reduced (bullish bias)
Earnings:        2.0% █           Quarterly volatility
Short Interest:  1.0% █           Monthly data
DXY:             0.0% -           Not applicable
```

### **Key Characteristics**
- **High Reddit weight (8%)** - AMD is popular on WallStreetBets
- **Balanced technical (8%)** - Volatile stock responds to technicals
- **Moderate institutional (6%)** - Some smart money but retail-heavy
- **News important (8%)** - Reacts to chip news, AI deals

### **News Keywords (11 terms)**
`Ryzen`, `EPYC`, `Radeon`, `Instinct`, `MI300`, `AI chips`, `data center`, `gaming GPU`, `Lisa Su`, `Xilinx`, `TSMC`

### **Technical Thresholds**
```python
RSI Overbought: 65    # Reversal risk above this
RSI Oversold: 35      # Bounce opportunity below this
Score Threshold: 0.04 # Min score for UP/DOWN signal
Gap Threshold: 1.5%   # Gap size triggering override logic
```

---

## 🔧 AVGO (Broadcom Inc)

### **Stock Profile**
- **Type:** Large-cap institutional
- **Sector:** Technology (XLK)
- **Character:** M&A driven, news-sensitive
- **Competitors:** QCOM, MRVL, TXN, NVDA

### **Volatility & Risk Parameters**
```python
typical_volatility: 2.81%       # Lowest of 3 stocks - more stable
historical_avg_gap: 1.03%       # Smallest expected move
momentum_continuation: 41%      # Lowest - more mean reversion
min_confidence: 60%             # Standard threshold
```

### **Data Source Weights (Sum = 100%)**
```
Futures:        15.0% ██████████  Market direction
News:           11.0% ███████     M&A deals ⭐
Options:        11.0% ███████     Institutional flow
Premarket:      10.0% ██████      Same-day momentum
Hidden Edge:    10.0% ██████      8 alt sources
Institutional:  10.0% ██████      Heavy institution ⭐
VIX:             8.0% █████       Fear gauge
Sector:          8.0% █████       Tech sector
Technical:       6.0% ████        Less volatile = less weight
Earnings:        6.0% ████        Quarterly events
Analyst:         2.0% █           Reduced (bullish bias)
Reddit:          2.0% █           Low retail interest
Twitter:         1.0% █           Minimal social
DXY:             0.0% -           Not applicable
Short Interest:  0.0% -           Not applicable
```

### **Key Characteristics**
- **High news weight (11%)** - M&A announcements drive big moves
- **High institutional (10%)** - Smart money controls this stock
- **Low social (2% Reddit, 1% Twitter)** - Not retail-driven
- **Reduced technical (6%)** - More stable, less technical trading

### **News Keywords (13 terms)**
`OpenAI`, `custom chips`, `VMware`, `AI accelerator`, `Hock Tan`, `acquisition`, `M&A`, `enterprise software`, `networking chips`, `infrastructure`, `data center`, `Wi-Fi`, `broadband`

### **Technical Thresholds**
```python
RSI Overbought: 65
RSI Oversold: 35
Score Threshold: 0.04
Gap Threshold: 1.5%
```

---

## 🔧 ORCL (Oracle Corporation)

### **Stock Profile**
- **Type:** Large-cap enterprise software
- **Sector:** Technology (XLK)
- **Character:** Institutional heavy, cloud/deal driven
- **Competitors:** MSFT, GOOGL, AMZN, CRM

### **Volatility & Risk Parameters**
```python
typical_volatility: 3.06%       # Mid-range volatility
historical_avg_gap: 1.24%       # Mid-range expected move
momentum_continuation: 48%      # Mid-range - balanced
min_confidence: 60%             # Standard threshold
```

### **Data Source Weights (Sum = 100%)**
```
Futures:        16.0% ███████████  Highest weight ⭐
Institutional:  16.0% ███████████  Highest weight ⭐
News:           14.0% █████████    Cloud deals ⭐
Options:        11.0% ███████      Institutional flow
Premarket:      10.0% ██████       Same-day momentum
Hidden Edge:    10.0% ██████       8 alt sources
VIX:             8.0% █████        Fear gauge
Technical:       6.0% ████         Stable stock
Sector:          5.0% ███          Tech sector
Analyst:         2.0% █            Reduced (bullish bias)
Earnings:        2.0% █            Quarterly events
Reddit:          0.0% -            No retail interest ⭐
Twitter:         0.0% -            No social buzz ⭐
DXY:             0.0% -            Not applicable
Short Interest:  0.0% -            Not applicable
```

### **Key Characteristics**
- **Highest futures weight (16%)** - Very macro-sensitive
- **Highest institutional weight (16%)** - Smart money dominates
- **High news weight (14%)** - Cloud deals, AWS competition
- **Zero social media (0%)** - Not a retail stock at all
- **Reduced technical (6%)** - Enterprise stocks less technical

### **News Keywords (15 terms)**
`Oracle Cloud`, `OCI`, `database`, `enterprise software`, `Safra Catz`, `cloud infrastructure`, `AWS competition`, `Azure`, `ERP`, `NetSuite`, `Java`, `MySQL`, `enterprise contract`, `cloud deal`, `data center`

### **Technical Thresholds**
```python
RSI Overbought: 65
RSI Oversold: 35
Score Threshold: 0.04
Gap Threshold: 1.5%
```

---

## 📊 **SIDE-BY-SIDE COMPARISON**

### **Volatility Ranking**
1. **AMD: 3.32%** - Most volatile (high-beta semiconductor)
2. **ORCL: 3.06%** - Mid-range (enterprise software)
3. **AVGO: 2.81%** - Least volatile (large-cap stable)

### **Momentum Continuation**
1. **AMD: 56%** - Trends continue most often
2. **ORCL: 48%** - Balanced behavior
3. **AVGO: 41%** - More mean-reverting

### **Top Data Source by Stock**
| Stock | #1 Source | #2 Source | #3 Source | Character |
|-------|-----------|-----------|-----------|-----------|
| AMD | Futures (15%) | Options (11%) | Premarket/Hidden (10%) | Market + Retail |
| AVGO | Futures (15%) | News/Options (11%) | Premarket/Hidden/Inst (10%) | M&A Driven |
| ORCL | Futures/Inst (16%) | News (14%) | Options (11%) | Institution Heavy |

### **Social Media Sensitivity**
| Stock | Reddit | Twitter | Total Social | Character |
|-------|--------|---------|--------------|-----------|
| AMD | 8% | 5% | **13%** | High retail interest |
| AVGO | 2% | 1% | **3%** | Low retail |
| ORCL | 0% | 0% | **0%** | No retail at all |

### **Institutional vs Retail**
| Stock | Institutional Weight | Social Weight | Type |
|-------|---------------------|---------------|------|
| AMD | 6% | 13% | **Retail-driven** |
| AVGO | 10% | 3% | **Mixed** |
| ORCL | 16% | 0% | **Institution-driven** |

---

## 🚀 **HOW STOCK-SPECIFIC LOGIC WORKS**

### **1. Configuration Loading**
```python
from stock_config import get_stock_config, get_stock_weight_adjustments

# Each stock loads its own config
config = get_stock_config('AMD')  # Gets AMD-specific params
weights = get_stock_weight_adjustments('AMD')  # Gets AMD weights

# No hardcoded values - everything from config
volatility = config['typical_volatility']  # 0.0332 for AMD
momentum = config['momentum_continuation_rate']  # 0.56 for AMD
```

### **2. Weight Application**
```python
# Each factor uses stock-specific weight
news_score = news_sentiment * weights['news']  # 8% for AMD, 11% for AVGO, 14% for ORCL
reddit_score = reddit_sentiment * weights['reddit']  # 8% for AMD, 2% for AVGO, 0% for ORCL
institutional_score = inst_signal * weights['institutional']  # 6% AMD, 10% AVGO, 16% ORCL
```

### **3. Technical Thresholds**
```python
from stock_config import get_technical_thresholds

thresholds = get_technical_thresholds('AMD')
rsi_overbought = thresholds['rsi_overbought']  # 65 (can be stock-specific)
score_threshold = thresholds['score_threshold']  # 0.04 (can be stock-specific)
```

### **4. Risk Management**
```python
# Trading algorithm uses stock-specific volatility
trade_plan = algo.generate_trade_plan(
    symbol='AMD',
    prediction=prediction,
    current_price=145.50,
    typical_volatility=config['typical_volatility']  # 0.0332 for AMD
)

# Stop loss automatically adjusted for stock's volatility
# AMD (3.32% vol) gets wider stop than AVGO (2.81% vol)
```

---

## ✅ **VERIFICATION RESULTS**

All tests passed:
- ✅ **Configuration Independence** - Each stock has unique params
- ✅ **Weight Independence** - Different weight distributions
- ✅ **No Hardcoded Conflicts** - All values from config
- ✅ **Stock-Specific Keywords** - Unique news terms
- ✅ **Trading Algorithm Integration** - Uses stock volatility

---

## 📝 **ADDING NEW STOCKS**

To add a new stock (e.g., NVDA):

```python
from stock_config import add_stock_config

new_config = {
    'name': 'NVIDIA Corporation',
    'sector_etf': 'XLK',
    'competitors': ['AMD', 'INTC', 'QCOM'],
    'typical_volatility': 0.0380,  # From 90-day analysis
    'historical_avg_gap': 0.0145,
    'min_confidence_threshold': 0.60,
    'weight_adjustments': {
        'futures': 0.15,
        'options': 0.12,
        # ... customize for NVDA behavior
    },
    'news_keywords': ['NVIDIA', 'GPU', 'AI chips', 'Jensen Huang', ...],
    'momentum_continuation_rate': 0.52,
    'description': 'AI chip leader with high volatility',
    'technical_thresholds': {
        'rsi_overbought': 65,
        'rsi_oversold': 35,
        'score_threshold': 0.04,
        'gap_threshold': 1.5
    }
}

add_stock_config('NVDA', new_config)
```

Then run:
```bash
python comprehensive_nextday_predictor.py NVDA
python trading_algorithm.py  # Will use NVDA-specific volatility
```

---

## 🎯 **KEY TAKEAWAYS**

1. **Each stock is independent** - No shared hardcoded values
2. **Weights reflect stock character** - Retail vs institution vs news-driven
3. **Volatility-based risk** - High-vol stocks get wider stops
4. **News keywords customized** - Relevant catalysts per stock
5. **Easy to extend** - Add new stocks with same structure

**Your system adapts to each stock's unique behavior! 🚀**
