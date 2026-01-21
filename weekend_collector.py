#!/usr/bin/env python3
"""
Weekend Data Collector
Collects news, sentiment, and futures data during weekends for Monday gap predictions
"""

import os
import sys
import time
import json
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pytz

# Import existing sentiment analysis from archived_systems
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'archived_systems'))
    from stock_predictor import StockPredictor
    PREDICTOR_AVAILABLE = True
except ImportError:
    StockPredictor = None
    PREDICTOR_AVAILABLE = False

# Import database for persistence
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))
    from replit_database_bridge import prediction_db
    DB_AVAILABLE = True
except ImportError:
    prediction_db = None
    DB_AVAILABLE = False

class WeekendCollector:
    """Collects weekend data for Monday gap predictions"""
    
    def __init__(self):
        self.et_tz = pytz.timezone('US/Eastern')
        self.predictor = StockPredictor() if PREDICTOR_AVAILABLE else None
        self.last_collection_time = None
        
    def run_cycle(self, target_date: Optional[datetime] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """Run a complete weekend data collection cycle with idempotence"""
        try:
            if target_date is None:
                # Default to next Monday
                current_time = datetime.now(self.et_tz)
                target_date = self._get_next_monday(current_time.date())
            
            # ENHANCED IDEMPOTENCE CHECK: Check if data exists AND is fresh enough
            existing_data = self.get_weekend_data(target_date)
            if existing_data and not force_refresh:
                collection_time_str = existing_data.get('collection_timestamp', '')
                if collection_time_str:
                    try:
                        # Parse the collection timestamp
                        collection_time = datetime.fromisoformat(collection_time_str.replace('Z', '+00:00'))
                        current_time = datetime.now(self.et_tz)
                        
                        # Check if data is older than 24 hours
                        time_diff = current_time - collection_time
                        hours_old = time_diff.total_seconds() / 3600
                        
                        if hours_old > 24:
                            print(f"⚠️ WEEKEND DATA IS STALE ({hours_old:.1f} hours old) - collecting fresh data")
                            print(f"📅 Old data collected at: {collection_time_str}")
                        else:
                            print(f"✅ WEEKEND DATA ALREADY EXISTS for {target_date}")
                            print(f"📅 Collected at: {collection_time_str} ({hours_old:.1f} hours ago)")
                            return existing_data
                    except Exception as e:
                        print(f"⚠️ Could not parse collection timestamp, collecting fresh data: {e}")
                else:
                    print(f"⚠️ No collection timestamp found, collecting fresh data")
            
            # THROTTLING: Don't collect more than once per hour
            if self.last_collection_time:
                time_since_last = datetime.now(self.et_tz) - self.last_collection_time
                if time_since_last.total_seconds() < 3600:  # 1 hour
                    minutes_ago = int(time_since_last.total_seconds() / 60)
                    print(f"⏰ THROTTLED: Last collection was {minutes_ago} minutes ago (wait 60 minutes)")
                    return {}
            
            print(f"🔄 WEEKEND COLLECTOR: Starting cycle for {target_date}")
            
            # Collect all weekend data with enhanced sources
            weekend_data = {
                'target_date': target_date.isoformat(),
                'collection_timestamp': datetime.now(self.et_tz).isoformat(),
                'news_sentiment': self._collect_news_sentiment(),
                'futures_data': self._collect_futures_data(),
                'crypto_sentiment': self._collect_crypto_sentiment(),
                'sector_analysis': self._collect_sector_analysis(),
                'economic_context': self._collect_economic_context(),
                'current_amd_price': self._get_current_amd_price()
            }
            
            # Persist the collected data
            self._persist_weekend_data(weekend_data)
            
            self.last_collection_time = datetime.now(self.et_tz)
            
            print(f"✅ WEEKEND COLLECTOR: Cycle completed, data persisted")
            return weekend_data
            
        except Exception as e:
            print(f"❌ WEEKEND COLLECTOR ERROR: {e}")
            return {}
    
    def _collect_news_sentiment(self) -> Dict[str, Any]:
        """Collect news and sentiment data"""
        try:
            if self.predictor and hasattr(self.predictor, 'get_enhanced_market_sentiment'):
                # Use existing sentiment analysis from StockPredictor
                sentiment_data = self.predictor.get_enhanced_market_sentiment()
                
                # Add weekend-specific news sources
                weekend_sentiment = {
                    'overall_score': sentiment_data.get('score', 0.0),
                    'impact_level': sentiment_data.get('impact_level', 'LOW'),
                    'breaking_news': sentiment_data.get('breaking_news', False),
                    'sources': sentiment_data.get('news_sources', []),
                    'confidence_boost': sentiment_data.get('confidence_boost', 0),
                    'collection_time': datetime.now(self.et_tz).isoformat()
                }
                
                print(f"📰 News sentiment: {sentiment_data.get('score', 0.0):+.2f} ({sentiment_data.get('impact_level', 'LOW')})")
                return weekend_sentiment
            else:
                # Fallback to basic sentiment collection
                return self._basic_sentiment_collection()
            
        except Exception as e:
            print(f"⚠️ News sentiment collection failed: {e}")
            return {'overall_score': 0.0, 'impact_level': 'LOW', 'error': str(e)}
    
    def _basic_sentiment_collection(self) -> Dict[str, Any]:
        """Enhanced sentiment collection using multiple free sources and advanced algorithms"""
        try:
            # Collect news from multiple free sources
            all_news = []
            sources_used = []
            
            # Source 1: Yahoo Finance News
            try:
                ticker = yf.Ticker('AMD')
                yf_news = ticker.news
                if yf_news:
                    all_news.extend(yf_news[:10])
                    sources_used.append('Yahoo Finance')
            except Exception as e:
                print(f"⚠️ Yahoo Finance news failed: {e}")
            
            # Source 2: Alpha Vantage Free Tier (if API key available)
            try:
                av_api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
                if av_api_key:
                    av_news = self._fetch_alpha_vantage_news(av_api_key)
                    if av_news:
                        all_news.extend(av_news)
                        sources_used.append('Alpha Vantage')
            except Exception as e:
                print(f"⚠️ Alpha Vantage news failed: {e}")
            
            # Source 3: Free RSS feeds (basic parsing)
            try:
                rss_news = self._fetch_free_rss_news()
                if rss_news:
                    all_news.extend(rss_news)
                    sources_used.append('RSS Feeds')
            except Exception as e:
                print(f"⚠️ RSS news failed: {e}")
            
            # Source 4: Finnhub (if API key available)
            try:
                finnhub_key = os.environ.get('FINNHUB_API_KEY')
                if finnhub_key:
                    finnhub_news = self._fetch_finnhub_news(finnhub_key)
                    if finnhub_news:
                        all_news.extend(finnhub_news)
                        sources_used.append('Finnhub')
            except Exception as e:
                print(f"⚠️ Finnhub news failed: {e}")
            
            if all_news:
                # Enhanced multi-layer sentiment analysis
                sentiment_score = self._enhanced_sentiment_analysis(all_news)
                impact_level = self._determine_impact_level(sentiment_score, len(all_news))
                
                return {
                    'overall_score': max(-1.0, min(1.0, sentiment_score)),
                    'impact_level': impact_level,
                    'breaking_news': self._detect_breaking_news(all_news),
                    'sources': sources_used,
                    'confidence_boost': min(len(sources_used) * 5, 20),  # Up to 20% boost for multiple sources
                    'collection_time': datetime.now(self.et_tz).isoformat(),
                    'method': 'enhanced_multi_source',
                    'articles_analyzed': len(all_news)
                }
            else:
                return {
                    'overall_score': 0.0,
                    'impact_level': 'LOW',
                    'breaking_news': False,
                    'sources': [],
                    'confidence_boost': 0,
                    'collection_time': datetime.now(self.et_tz).isoformat(),
                    'method': 'no_news_available'
                }
            
        except Exception as e:
            return {
                'overall_score': 0.0,
                'impact_level': 'LOW',
                'error': str(e),
                'collection_time': datetime.now(self.et_tz).isoformat()
            }
    
    def _collect_futures_data(self) -> Dict[str, Any]:
        """Collect futures data for overnight sentiment"""
        try:
            futures_symbols = {
                'ES=F': 'S&P 500 Futures',
                'NQ=F': 'NASDAQ Futures', 
                '^VIX': 'VIX Futures',
                'CL=F': 'Oil Futures'
            }
            
            futures_data = {}
            overall_sentiment = 0.0
            
            for symbol, name in futures_symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="5d")
                    
                    if not data.empty:
                        current_price = float(data['Close'].iloc[-1])
                        previous_close = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
                        change_pct = ((current_price - previous_close) / previous_close) * 100
                        
                        futures_data[symbol] = {
                            'name': name,
                            'current_price': current_price,
                            'change_pct': change_pct,
                            'change_direction': 'UP' if change_pct > 0 else 'DOWN' if change_pct < 0 else 'FLAT'
                        }
                        
                        # Add to overall sentiment (VIX is inverse)
                        if 'VIX' in symbol or '^VIX' in symbol:
                            overall_sentiment -= change_pct * 0.2  # Inverse VIX
                        else:
                            overall_sentiment += change_pct * 0.3
                            
                except Exception as e:
                    print(f"⚠️ Failed to fetch {symbol}: {e}")
                    futures_data[symbol] = {'error': str(e)}
            
            futures_result = {
                'individual_futures': futures_data,
                'overall_sentiment': overall_sentiment,
                'sentiment_direction': 'BULLISH' if overall_sentiment > 0.5 else 'BEARISH' if overall_sentiment < -0.5 else 'NEUTRAL',
                'collection_time': datetime.now(self.et_tz).isoformat()
            }
            
            print(f"📈 Futures sentiment: {overall_sentiment:+.2f}% ({futures_result['sentiment_direction']})")
            return futures_result
            
        except Exception as e:
            print(f"⚠️ Futures data collection failed: {e}")
            return {'overall_sentiment': 0.0, 'error': str(e)}
    
    def _collect_crypto_sentiment(self) -> Dict[str, Any]:
        """Collect crypto data as risk sentiment proxy"""
        try:
            crypto_symbols = ['BTC-USD', 'ETH-USD']
            crypto_data = {}
            overall_crypto_sentiment = 0.0
            
            for symbol in crypto_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="3d")
                    
                    if not data.empty:
                        current_price = float(data['Close'].iloc[-1])
                        previous_close = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
                        change_pct = ((current_price - previous_close) / previous_close) * 100
                        
                        crypto_data[symbol] = {
                            'current_price': current_price,
                            'change_pct': change_pct
                        }
                        
                        overall_crypto_sentiment += change_pct * 0.1  # Small weight for crypto
                        
                except Exception as e:
                    crypto_data[symbol] = {'error': str(e)}
            
            crypto_result = {
                'individual_crypto': crypto_data,
                'overall_sentiment': overall_crypto_sentiment,
                'risk_sentiment': 'RISK_ON' if overall_crypto_sentiment > 1.0 else 'RISK_OFF' if overall_crypto_sentiment < -1.0 else 'NEUTRAL',
                'collection_time': datetime.now(self.et_tz).isoformat()
            }
            
            print(f"₿ Crypto sentiment: {overall_crypto_sentiment:+.2f}% ({crypto_result['risk_sentiment']})")
            return crypto_result
            
        except Exception as e:
            print(f"⚠️ Crypto data collection failed: {e}")
            return {'overall_sentiment': 0.0, 'error': str(e)}
    
    def _collect_economic_context(self) -> Dict[str, Any]:
        """Collect economic context for weekend"""
        try:
            # Use existing economic data engine if available
            if hasattr(self.predictor, 'economic_engine') and self.predictor.economic_engine:
                economic_data = self.predictor.economic_engine.get_economic_indicators()
                return {
                    'has_economic_data': True,
                    'economic_sentiment': economic_data.get('economic_sentiment_score', 0.0),
                    'key_indicators': economic_data.get('indicators', {}),
                    'collection_time': datetime.now(self.et_tz).isoformat()
                }
            else:
                return {
                    'has_economic_data': False,
                    'note': 'Economic data engine not available',
                    'collection_time': datetime.now(self.et_tz).isoformat()
                }
                
        except Exception as e:
            return {
                'has_economic_data': False,
                'error': str(e),
                'collection_time': datetime.now(self.et_tz).isoformat()
            }
    
    def _collect_sector_analysis(self) -> Dict[str, Any]:
        """Collect semiconductor sector analysis for AMD context"""
        try:
            # Key semiconductor and tech sector indicators
            sector_symbols = {
                'SOXX': 'Semiconductor ETF',
                'SMH': 'Semiconductor Holders ETF',
                'NVDA': 'NVIDIA (Peer)',
                'INTC': 'Intel (Peer)',
                'QQQ': 'Tech Sector'
            }
            
            sector_data = {}
            overall_sector_score = 0.0
            valid_count = 0
            
            for symbol, name in sector_symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="5d")
                    
                    if not data.empty and len(data) >= 2:
                        current_price = float(data['Close'].iloc[-1])
                        previous_close = float(data['Close'].iloc[-2])
                        change_pct = ((current_price - previous_close) / previous_close) * 100
                        
                        # Calculate 5-day trend strength
                        five_day_change = ((current_price - float(data['Close'].iloc[0])) / float(data['Close'].iloc[0])) * 100
                        
                        sector_data[symbol] = {
                            'name': name,
                            'current_price': current_price,
                            'daily_change_pct': change_pct,
                            'five_day_change_pct': five_day_change,
                            'trend': 'UP' if five_day_change > 0 else 'DOWN'
                        }
                        
                        # Weight sector indicators
                        if symbol in ['SOXX', 'SMH']:
                            weight = 0.35  # Semiconductor sector gets highest weight
                        elif symbol == 'NVDA':
                            weight = 0.20  # NVIDIA is key AMD peer
                        elif symbol == 'QQQ':
                            weight = 0.15  # Tech sector context
                        else:
                            weight = 0.10  # Intel gets lower weight
                        
                        overall_sector_score += change_pct * weight
                        valid_count += 1
                        
                except Exception as e:
                    print(f"⚠️ Failed to fetch {symbol}: {e}")
                    sector_data[symbol] = {'error': str(e)}
            
            # Normalize sector score
            if valid_count > 0:
                overall_sector_score = overall_sector_score / (valid_count / len(sector_symbols))
            
            sector_result = {
                'individual_sectors': sector_data,
                'overall_score': overall_sector_score,
                'sector_trend': 'BULLISH' if overall_sector_score > 0.3 else 'BEARISH' if overall_sector_score < -0.3 else 'NEUTRAL',
                'data_quality': f"{valid_count}/{len(sector_symbols)} sources",
                'collection_time': datetime.now(self.et_tz).isoformat()
            }
            
            print(f"🏭 Sector sentiment: {overall_sector_score:+.2f}% ({sector_result['sector_trend']})")
            return sector_result
            
        except Exception as e:
            print(f"⚠️ Sector analysis failed: {e}")
            return {'overall_score': 0.0, 'error': str(e)}
    
    def _get_current_amd_price(self) -> Optional[float]:
        """Get current AMD price for prediction calculations"""
        try:
            ticker = yf.Ticker('AMD')
            data = ticker.history(period="1d")
            
            if not data.empty:
                current_price = float(data['Close'].iloc[-1])
                print(f"💰 Current AMD price: ${current_price:.2f}")
                return current_price
            else:
                print(f"⚠️ No AMD price data available")
                return None
                
        except Exception as e:
            print(f"⚠️ Failed to get AMD price: {e}")
            return None
    
    def _persist_weekend_data(self, data: Dict[str, Any]) -> None:
        """Persist weekend data to database/file"""
        try:
            if DB_AVAILABLE and prediction_db:
                # Store in database with target_date as key
                key = f"weekend_data_{data['target_date']}"
                # Fix: Use the correct method name
                if hasattr(prediction_db, 'set'):
                    prediction_db.set(key, json.dumps(data))
                    print(f"💾 Weekend data stored in database: {key}")
                else:
                    # Fallback to file if database method not available
                    raise AttributeError("Database set method not available")
            else:
                # Store in file as fallback
                os.makedirs('data/weekend', exist_ok=True)
                filename = f"data/weekend/weekend_data_{data['target_date']}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"💾 Weekend data stored in file: {filename}")
                
        except Exception as e:
            print(f"⚠️ Failed to persist weekend data: {e}")
            # Always ensure file fallback works
            try:
                os.makedirs('data/weekend', exist_ok=True)
                filename = f"data/weekend/weekend_data_{data['target_date']}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"💾 Weekend data stored in file (fallback): {filename}")
            except Exception as e2:
                print(f"❌ Complete storage failure: {e2}")
    
    def get_weekend_data(self, target_date: datetime) -> Optional[Dict[str, Any]]:
        """Retrieve stored weekend data for target date"""
        try:
            target_str = target_date.isoformat() if hasattr(target_date, 'isoformat') else str(target_date)
            
            if DB_AVAILABLE and prediction_db:
                key = f"weekend_data_{target_str}"
                # Fix: Use the correct method name
                if hasattr(prediction_db, 'get'):
                    data_str = prediction_db.get(key)
                    if data_str:
                        return json.loads(data_str)
                elif hasattr(prediction_db, 'get_data'):
                    data = prediction_db.get_data(key)
                    if data:
                        return data
            
            # Try file fallback
            filename = f"data/weekend/weekend_data_{target_str}.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Failed to retrieve weekend data: {e}")
            return None
    
    def _fetch_alpha_vantage_news(self, api_key: str) -> List[Dict]:
        """Fetch news from Alpha Vantage free tier API"""
        try:
            if not api_key:
                return []
                
            import urllib.request
            import urllib.parse
            
            # Alpha Vantage NEWS_SENTIMENT endpoint (free tier)
            base_url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': 'AMD',
                'apikey': api_key,
                'limit': 50
            }
            
            url = f"{base_url}?" + urllib.parse.urlencode(params)
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read())
                
            feed = data.get('feed', [])
            news_articles = []
            
            for article in feed[:10]:  # Limit to 10 articles
                news_articles.append({
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'sentiment_score': float(article.get('overall_sentiment_score', 0)),
                    'relevance_score': float(article.get('relevance_score', 0)),
                    'source': 'Alpha Vantage',
                    'published': article.get('time_published', '')
                })
            
            print(f"📊 Alpha Vantage: Retrieved {len(news_articles)} articles")
            return news_articles
            
        except Exception as e:
            print(f"⚠️ Alpha Vantage API failed: {e}")
            return []
    
    def _fetch_free_rss_news(self) -> List[Dict]:
        """Fetch news from free RSS feeds"""
        try:
            import urllib.request
            import re
            
            # Free RSS feeds for financial news
            rss_feeds = [
                'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'https://www.marketwatch.com/rss/headlines'
            ]
            
            news_articles = []
            
            for feed_url in rss_feeds:
                try:
                    with urllib.request.urlopen(feed_url, timeout=8) as response:
                        rss_content = response.read().decode('utf-8')
                    
                    # Simple RSS parsing using regex (basic but effective)
                    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', rss_content)
                    if not titles:
                        titles = re.findall(r'<title>(.*?)</title>', rss_content)
                    
                    descriptions = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', rss_content)
                    if not descriptions:
                        descriptions = re.findall(r'<description>(.*?)</description>', rss_content)
                    
                    # Filter for AMD-related news
                    for i, title in enumerate(titles[:5]):
                        if any(keyword in title.lower() for keyword in ['amd', 'advanced micro', 'semiconductor', 'chip', 'ai']):
                            news_articles.append({
                                'title': title,
                                'summary': descriptions[i] if i < len(descriptions) else '',
                                'source': 'RSS',
                                'published': datetime.now().isoformat()
                            })
                            
                except Exception as e:
                    print(f"⚠️ RSS feed {feed_url} failed: {e}")
                    continue
            
            print(f"📡 RSS: Retrieved {len(news_articles)} AMD-related articles")
            return news_articles
            
        except Exception as e:
            print(f"⚠️ RSS news collection failed: {e}")
            return []
    
    def _fetch_finnhub_news(self, api_key: str) -> List[Dict]:
        """Fetch news from Finnhub API"""
        try:
            if not api_key:
                return []
            
            try:
                import requests
            except ImportError:
                print("⚠️ requests library not available for Finnhub")
                return []
            
            # Finnhub company news endpoint
            url = f"https://finnhub.io/api/v1/company-news"
            
            # Get news from last 7 days
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                'symbol': 'AMD',
                'from': from_date,
                'to': to_date,
                'token': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                news_data = response.json()
                news_articles = []
                
                for article in news_data[:15]:  # Limit to 15 articles
                    # Finnhub sentiment is -1 to 1
                    sentiment = article.get('sentiment', 0)
                    
                    news_articles.append({
                        'title': article.get('headline', ''),
                        'summary': article.get('summary', ''),
                        'sentiment_score': float(sentiment),
                        'source': article.get('source', 'Finnhub'),
                        'published': article.get('datetime', ''),
                        'url': article.get('url', '')
                    })
                
                print(f"🐟 Finnhub: Retrieved {len(news_articles)} articles")
                return news_articles
            else:
                print(f"⚠️ Finnhub API returned status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"⚠️ Finnhub API failed: {e}")
            return []
    
    def _enhanced_sentiment_analysis(self, news_articles: List[Dict]) -> float:
        """Advanced sentiment analysis using multiple techniques"""
        try:
            if not news_articles:
                return 0.0
            
            total_score = 0.0
            total_weight = 0.0
            
            # Enhanced keyword lists with weights
            strong_positive = ['breakthrough', 'surge', 'soar', 'rocket', 'explode', 'massive', 'revolutionary']
            positive = ['upgrade', 'beat', 'strong', 'growth', 'positive', 'buy', 'bullish', 'rally', 'rise']
            neutral_positive = ['stable', 'maintain', 'hold', 'steady', 'continue']
            neutral_negative = ['uncertain', 'mixed', 'volatile', 'cautious']
            negative = ['downgrade', 'miss', 'weak', 'decline', 'negative', 'sell', 'bearish', 'fall', 'drop']
            strong_negative = ['crash', 'plummet', 'collapse', 'disaster', 'terrible', 'catastrophic']
            
            # AMD-specific keywords
            amd_positive = ['ai leadership', 'data center growth', 'market share gain', 'chip performance', 'innovation']
            amd_negative = ['intel competition', 'nvidia threat', 'market share loss', 'supply chain', 'shortage']
            
            for article in news_articles:
                # Get article text
                text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
                
                # Use Alpha Vantage sentiment if available
                if 'sentiment_score' in article and article['sentiment_score'] != 0:
                    av_score = float(article['sentiment_score'])
                    relevance = float(article.get('relevance_score', 0.5))
                    weight = relevance * 2.0  # Higher weight for Alpha Vantage
                    total_score += av_score * weight
                    total_weight += weight
                    continue
                
                # Enhanced keyword analysis
                article_score = 0.0
                
                # Strong signals
                article_score += sum(3.0 for word in strong_positive if word in text)
                article_score -= sum(3.0 for word in strong_negative if word in text)
                
                # Regular signals  
                article_score += sum(1.0 for word in positive if word in text)
                article_score -= sum(1.0 for word in negative if word in text)
                
                # Neutral signals
                article_score += sum(0.3 for word in neutral_positive if word in text)
                article_score -= sum(0.3 for word in neutral_negative if word in text)
                
                # AMD-specific signals (higher weight)
                article_score += sum(2.0 for phrase in amd_positive if phrase in text)
                article_score -= sum(2.0 for phrase in amd_negative if phrase in text)
                
                # Context analysis - negation detection
                if ' not ' in text or " n't " in text or 'however' in text:
                    article_score *= 0.5  # Reduce impact for negated statements
                
                # Recency weight (newer articles get higher weight)
                recency_weight = 1.0
                if 'published' in article:
                    try:
                        pub_time = datetime.fromisoformat(article['published'].replace('Z', '+00:00'))
                        hours_old = (datetime.now(self.et_tz) - pub_time).total_seconds() / 3600
                        recency_weight = max(0.3, 1.0 - (hours_old / 72))  # Decay over 3 days
                    except:
                        pass
                
                # Source credibility weight
                source_weight = 1.0
                source = article.get('source', '').lower()
                if 'alpha vantage' in source:
                    source_weight = 2.0
                elif 'yahoo' in source:
                    source_weight = 1.5
                elif 'reuters' in source:
                    source_weight = 1.8
                elif 'rss' in source:
                    source_weight = 1.2
                
                final_weight = recency_weight * source_weight
                total_score += article_score * final_weight
                total_weight += final_weight
            
            # Calculate weighted average
            if total_weight > 0:
                final_score = total_score / total_weight
                # Normalize to [-1, 1] range with soft scaling
                final_score = max(-1.0, min(1.0, final_score * 0.1))
            else:
                final_score = 0.0
            
            print(f"📊 Enhanced sentiment: {final_score:+.3f} from {len(news_articles)} articles")
            return final_score
            
        except Exception as e:
            print(f"⚠️ Enhanced sentiment analysis failed: {e}")
            return 0.0
    
    def _determine_impact_level(self, sentiment_score: float, article_count: int) -> str:
        """Determine impact level based on sentiment and article volume"""
        try:
            abs_score = abs(sentiment_score)
            
            # High impact: Strong sentiment with many articles
            if abs_score > 0.6 and article_count >= 5:
                return 'HIGH'
            elif abs_score > 0.4 and article_count >= 8:
                return 'HIGH'
            
            # Medium impact: Moderate sentiment or fewer articles
            elif abs_score > 0.3 and article_count >= 3:
                return 'MEDIUM'
            elif abs_score > 0.5 and article_count >= 1:
                return 'MEDIUM'
            
            # Low impact: Weak sentiment or few articles
            else:
                return 'LOW'
                
        except Exception:
            return 'LOW'
    
    def _detect_breaking_news(self, news_articles: List[Dict]) -> bool:
        """Detect if there's breaking news that could impact markets"""
        try:
            breaking_keywords = [
                'breaking', 'urgent', 'alert', 'just in', 'developing',
                'merger', 'acquisition', 'earnings', 'beat', 'miss',
                'ceo', 'lawsuit', 'investigation', 'recall', 'guidance',
                'partnership', 'deal', 'contract', 'breakthrough'
            ]
            
            recent_cutoff = datetime.now(self.et_tz) - timedelta(hours=6)
            
            for article in news_articles:
                title_summary = f"{article.get('title', '')} {article.get('summary', '')}".lower()
                
                # Check for breaking news keywords
                if any(keyword in title_summary for keyword in breaking_keywords):
                    # Check if it's recent
                    try:
                        if 'published' in article:
                            pub_time = datetime.fromisoformat(article['published'].replace('Z', '+00:00'))
                            if pub_time > recent_cutoff:
                                return True
                    except:
                        # If we can't parse time, assume it might be recent
                        return True
            
            return False
            
        except Exception:
            return False

    def _get_next_monday(self, current_date) -> datetime:
        """Get next Monday from current date"""
        days_ahead = 7 - current_date.weekday()  # Monday is 0
        if days_ahead == 7:  # If today is Monday
            days_ahead = 7
        return current_date + timedelta(days=days_ahead)

# Global weekend collector instance
weekend_collector = WeekendCollector()