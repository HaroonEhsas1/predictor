#!/usr/bin/env python3
"""
ENHANCED SENTIMENT ANALYSIS ENGINE
Advanced NLP-based sentiment analysis for financial news
Replaces basic keyword matching with sophisticated analysis
"""

import re
import json
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf

class AdvancedSentimentAnalyzer:
    """
    Advanced sentiment analysis engine that moves beyond basic keyword matching
    Features:
    1. Advanced NLP techniques (context analysis, negation handling, intensifiers)
    2. Multiple diverse news sources 
    3. Sophisticated mathematical weighting with machine learning principles
    4. Financial domain-specific sentiment scoring
    """
    
    def __init__(self, symbol="AMD"):
        self.symbol = symbol
        
        # Try to use local transformer-based analysis first
        try:
            from local_transformer_sentiment import LocalTransformerSentiment
            self.transformer_analyzer = LocalTransformerSentiment(symbol)
            self.use_transformers = True
            print("🤖 LOCAL TRANSFORMER ENGINE: Advanced sentiment models loaded")
        except ImportError as e:
            print(f"⚠️ Local transformer models unavailable: {str(e)[:50]}")
            self.transformer_analyzer = None
            self.use_transformers = False
        
        self.initialize_advanced_lexicons()
        self.initialize_news_sources()
        
    def initialize_advanced_lexicons(self):
        """Initialize advanced financial sentiment lexicons with context weights"""
        
        # Financial sentiment lexicon with intensity scores
        self.financial_sentiment_lexicon = {
            # Strong positive (0.8-1.0)
            'breakthrough': 0.9, 'surge': 0.9, 'skyrocket': 1.0, 'soar': 0.9,
            'outstanding': 0.8, 'exceptional': 0.8, 'extraordinary': 0.9,
            'robust': 0.8, 'stellar': 0.9, 'phenomenal': 0.9,
            
            # Moderate positive (0.4-0.7)
            'growth': 0.6, 'positive': 0.5, 'gain': 0.6, 'increase': 0.5,
            'beat': 0.7, 'exceed': 0.7, 'outperform': 0.7, 'strong': 0.6,
            'revenue': 0.4, 'profit': 0.6, 'expansion': 0.6,
            
            # Weak positive (0.1-0.3)
            'stable': 0.2, 'steady': 0.2, 'maintained': 0.1, 'hold': 0.1,
            
            # Weak negative (-0.1 to -0.3)
            'concern': -0.2, 'caution': -0.2, 'uncertainty': -0.3, 'risk': -0.2,
            
            # Moderate negative (-0.4 to -0.7)
            'decline': -0.5, 'drop': -0.5, 'fall': -0.5, 'weak': -0.6,
            'miss': -0.7, 'underperform': -0.7, 'loss': -0.6, 'cut': -0.6,
            'challenge': -0.5, 'struggle': -0.6, 'pressure': -0.5,
            
            # Strong negative (-0.8 to -1.0)
            'plummet': -0.9, 'crash': -1.0, 'collapse': -1.0, 'devastating': -0.9,
            'crisis': -0.8, 'disaster': -0.9, 'catastrophic': -1.0,
            'downgrade': -0.8, 'disappointing': -0.7
        }
        
        # Intensifiers that modify sentiment strength
        self.intensifiers = {
            'very': 1.3, 'extremely': 1.5, 'highly': 1.3, 'significantly': 1.4,
            'substantially': 1.4, 'greatly': 1.3, 'remarkably': 1.4,
            'moderately': 1.1, 'slightly': 0.8, 'somewhat': 0.9, 'rather': 1.1
        }
        
        # Negation words that flip sentiment
        self.negations = {
            'not', 'no', 'never', 'nothing', 'neither', 'nor', 'none', 'nobody',
            'nowhere', 'cannot', 'cant', 'couldnt', 'shouldnt', 'wouldnt',
            'doesnt', 'didnt', 'wont', 'isnt', 'arent', 'wasnt', 'werent',
            'hasnt', 'havent', 'hadnt', 'without', 'lack', 'lacking', 'failed'
        }
        
        # Context-specific financial terms
        self.financial_context_multipliers = {
            'earnings': 1.4, 'revenue': 1.3, 'guidance': 1.5, 'forecast': 1.3,
            'outlook': 1.4, 'projection': 1.2, 'analyst': 1.3, 'rating': 1.4,
            'target': 1.2, 'estimate': 1.1, 'consensus': 1.2
        }
        
    def initialize_news_sources(self):
        """Initialize multiple diverse news sources beyond Yahoo Finance"""
        self.news_sources = [
            {
                'name': 'Yahoo Finance',
                'method': self._fetch_yahoo_finance_news,
                'reliability_weight': 0.8,
                'update_frequency': 'real-time'
            },
            {
                'name': 'MarketWatch RSS',
                'method': self._fetch_marketwatch_rss,
                'reliability_weight': 0.85,
                'update_frequency': 'hourly'
            },
            {
                'name': 'Seeking Alpha RSS',
                'method': self._fetch_seeking_alpha_rss,
                'reliability_weight': 0.8,
                'update_frequency': 'hourly'
            },
            {
                'name': 'Financial Times RSS',
                'method': self._fetch_ft_rss,
                'reliability_weight': 0.9,
                'update_frequency': 'real-time'
            },
            {
                'name': 'Reuters Business RSS',
                'method': self._fetch_reuters_rss,
                'reliability_weight': 0.95,
                'update_frequency': 'real-time'
            },
            {
                'name': 'Bloomberg RSS',
                'method': self._fetch_bloomberg_rss,
                'reliability_weight': 0.9,
                'update_frequency': 'real-time'
            },
            {
                'name': 'CNBC RSS',
                'method': self._fetch_cnbc_rss,
                'reliability_weight': 0.8,
                'update_frequency': 'real-time'
            },
            {
                'name': 'Alpha Vantage News',
                'method': self._fetch_alpha_vantage_news,
                'reliability_weight': 0.9,
                'update_frequency': 'hourly'
            }
        ]
        
    def analyze_advanced_sentiment(self, max_news_items=50) -> Dict:
        """
        Advanced sentiment analysis using transformer models or sophisticated NLP fallback
        Returns comprehensive sentiment analysis with confidence scores
        """
        try:
            # Use transformer-based analysis if available (primary method)
            if self.use_transformers and self.transformer_analyzer:
                print("🤖 TRANSFORMER SENTIMENT: Using FinBERT & RoBERTa models...")
                
                # Get news from multiple sources
                all_news_data = []
                source_results = {}
                
                for source_config in self.news_sources:
                    try:
                        print(f"📰 Fetching from {source_config['name']}...")
                        news_items = source_config['method']()
                        if news_items:
                            weighted_items = [
                                {**item, 'source_weight': source_config['reliability_weight']} 
                                for item in news_items[:max_news_items//len(self.news_sources)]
                            ]
                            all_news_data.extend(weighted_items)
                            source_results[source_config['name']] = len(weighted_items)
                            print(f"✅ {source_config['name']}: {len(weighted_items)} items")
                        else:
                            source_results[source_config['name']] = 0
                            print(f"❌ {source_config['name']}: No items found")
                    except Exception as e:
                        source_results[source_config['name']] = 0
                        print(f"⚠️ {source_config['name']}: Error - {str(e)[:50]}")
                
                if all_news_data:
                    # Use transformer analysis
                    transformer_result = self.transformer_analyzer.analyze_news_batch(all_news_data, max_news_items)
                    transformer_result['source_breakdown'] = source_results
                    return transformer_result
                else:
                    return self._get_fallback_sentiment("No news data available from any source")
            
            # Fallback to advanced lexicon-based analysis
            print("🧠 ENHANCED SENTIMENT ANALYSIS: Using advanced NLP techniques (fallback)...")
            
            all_news_data = []
            source_results = {}
            
            # Collect news from multiple sources
            for source_config in self.news_sources:
                try:
                    print(f"📰 Fetching from {source_config['name']}...")
                    news_items = source_config['method']()
                    
                    if news_items:
                        # Apply reliability weighting
                        weighted_items = [
                            {**item, 'source_weight': source_config['reliability_weight']} 
                            for item in news_items[:max_news_items//len(self.news_sources)]
                        ]
                        all_news_data.extend(weighted_items)
                        source_results[source_config['name']] = len(weighted_items)
                        print(f"✅ {source_config['name']}: {len(weighted_items)} articles")
                    else:
                        print(f"⚠️ {source_config['name']}: No articles retrieved")
                        source_results[source_config['name']] = 0
                        
                except Exception as e:
                    print(f"❌ {source_config['name']} failed: {str(e)[:50]}")
                    source_results[source_config['name']] = 0
            
            if not all_news_data:
                return self._get_fallback_sentiment("No news data available from any source")
            
            # Advanced sentiment analysis on collected data
            sentiment_scores = []
            detailed_analysis = []
            
            for news_item in all_news_data:
                analysis = self._analyze_single_article_advanced(news_item)
                if analysis['confidence'] > 0.3:  # Only include confident predictions
                    sentiment_scores.append(analysis)
                    detailed_analysis.append(analysis)
            
            # Calculate weighted overall sentiment
            overall_result = self._calculate_weighted_sentiment(sentiment_scores)
            overall_result['source_breakdown'] = source_results
            overall_result['total_articles_analyzed'] = len(sentiment_scores)
            overall_result['detailed_analysis'] = detailed_analysis[:10]  # Top 10 for review
            
            print(f"📊 Advanced analysis complete: {len(sentiment_scores)} articles, overall sentiment: {overall_result['overall_score']:.3f}")
            return overall_result
            
        except Exception as e:
            print(f"❌ Enhanced sentiment analysis failed: {str(e)}")
            return self._get_fallback_sentiment(f"Analysis error: {str(e)[:30]}")
    
    def _analyze_single_article_advanced(self, news_item: Dict) -> Dict:
        """
        Advanced single article analysis using sophisticated NLP techniques
        """
        try:
            title = news_item.get('title', '')
            content = news_item.get('content', '')
            summary = news_item.get('summary', '')
            
            # Combine all text with title weighted higher
            full_text = f"{title} {title} {summary} {content}".lower()
            
            if not full_text.strip():
                return {'sentiment_score': 0.0, 'confidence': 0.0, 'reasoning': 'No content'}
            
            # Step 1: Basic sentiment scoring with advanced lexicon
            lexicon_score = self._calculate_lexicon_sentiment(full_text)
            
            # Step 2: Context and negation analysis
            context_adjusted_score = self._apply_context_analysis(full_text, lexicon_score)
            
            # Step 3: Financial domain adjustments
            domain_adjusted_score = self._apply_financial_domain_adjustments(full_text, context_adjusted_score)
            
            # Step 4: AMD-specific event detection
            amd_specific_score = self._detect_amd_specific_events(full_text)
            
            # Step 5: Recency and source reliability weighting
            source_weight = news_item.get('source_weight', 0.5)
            recency_weight = self._calculate_recency_weight(news_item.get('timestamp'))
            
            # Final weighted sentiment calculation
            final_score = (
                domain_adjusted_score * 0.4 +
                amd_specific_score * 0.4 +
                lexicon_score * 0.2
            ) * source_weight * recency_weight
            
            # Calculate confidence based on multiple factors
            confidence = self._calculate_confidence(
                full_text, lexicon_score, domain_adjusted_score, 
                amd_specific_score, source_weight
            )
            
            return {
                'sentiment_score': np.clip(final_score, -1.0, 1.0),
                'confidence': confidence,
                'lexicon_score': lexicon_score,
                'context_adjusted': context_adjusted_score,
                'domain_adjusted': domain_adjusted_score,
                'amd_specific': amd_specific_score,
                'source_weight': source_weight,
                'recency_weight': recency_weight,
                'title': title[:100],
                'reasoning': self._generate_reasoning(
                    lexicon_score, context_adjusted_score, 
                    domain_adjusted_score, amd_specific_score
                )
            }
            
        except Exception as e:
            return {'sentiment_score': 0.0, 'confidence': 0.0, 'reasoning': f'Analysis error: {str(e)[:30]}'}
    
    def _calculate_lexicon_sentiment(self, text: str) -> float:
        """Calculate sentiment using advanced financial lexicon with intensifiers"""
        words = re.findall(r'\b\w+\b', text.lower())
        total_score = 0.0
        word_count = 0
        
        for i, word in enumerate(words):
            if word in self.financial_sentiment_lexicon:
                base_score = self.financial_sentiment_lexicon[word]
                
                # Check for intensifiers in previous words
                intensifier_multiplier = 1.0
                for j in range(max(0, i-2), i):
                    if words[j] in self.intensifiers:
                        intensifier_multiplier = max(intensifier_multiplier, self.intensifiers[words[j]])
                
                # Check for negations in previous words
                negation_detected = False
                for j in range(max(0, i-3), i):
                    if words[j] in self.negations:
                        negation_detected = True
                        break
                
                # Apply transformations
                final_score = base_score * intensifier_multiplier
                if negation_detected:
                    final_score = -final_score
                
                total_score += final_score
                word_count += 1
        
        return total_score / max(word_count, 1) if word_count > 0 else 0.0
    
    def _apply_context_analysis(self, text: str, base_score: float) -> float:
        """Apply financial context analysis to adjust sentiment"""
        context_multiplier = 1.0
        
        # Look for financial context terms
        for term, multiplier in self.financial_context_multipliers.items():
            if term in text:
                context_multiplier = max(context_multiplier, multiplier)
        
        # Check for conditional/uncertain language that reduces confidence
        uncertainty_terms = ['may', 'might', 'could', 'possibly', 'potentially', 'uncertain', 'unclear']
        uncertainty_count = sum(1 for term in uncertainty_terms if term in text)
        uncertainty_dampener = max(0.7, 1.0 - (uncertainty_count * 0.1))
        
        return base_score * context_multiplier * uncertainty_dampener
    
    def _apply_financial_domain_adjustments(self, text: str, base_score: float) -> float:
        """Apply AMD and semiconductor industry specific adjustments"""
        
        # AMD-specific positive indicators
        amd_positive_patterns = [
            r'amd.*beat.*estimate', r'amd.*revenue.*growth', r'amd.*market.*share',
            r'epyc.*growth', r'ryzen.*sales', r'data.*center.*revenue',
            r'amd.*partnership', r'amd.*deal', r'amd.*wins'
        ]
        
        # AMD-specific negative indicators  
        amd_negative_patterns = [
            r'amd.*miss.*estimate', r'amd.*revenue.*decline', r'amd.*guidance.*lower',
            r'china.*restriction.*amd', r'export.*ban.*amd', r'trade.*war.*amd',
            r'nvidia.*compete.*amd', r'intel.*threat.*amd'
        ]
        
        adjustment = 0.0
        
        # Check positive patterns
        for pattern in amd_positive_patterns:
            if re.search(pattern, text):
                adjustment += 0.2
        
        # Check negative patterns
        for pattern in amd_negative_patterns:
            if re.search(pattern, text):
                adjustment -= 0.3
        
        return base_score + adjustment
    
    def _detect_amd_specific_events(self, text: str) -> float:
        """Detect AMD-specific events with sophisticated pattern matching"""
        
        event_scores = {
            # Product launches (positive)
            r'mi\d+.*launch': 0.6,
            r'epyc.*announce': 0.5,
            r'ryzen.*release': 0.4,
            r'radeon.*unveil': 0.4,
            
            # Partnerships (positive)
            r'amd.*microsoft': 0.7,
            r'amd.*google': 0.6,
            r'amd.*meta': 0.6,
            r'amd.*openai': 0.8,
            
            # Competitive wins (positive)
            r'amd.*nvidia.*alternative': 0.5,
            r'amd.*cuda.*competitor': 0.6,
            r'amd.*market.*share.*gain': 0.7,
            
            # Regulatory issues (negative)
            r'china.*ban.*amd': -0.8,
            r'export.*restriction.*amd': -0.7,
            r'trade.*war.*amd': -0.6,
            r'bis.*entity.*list.*amd': -0.9,
            
            # Executive changes (negative)
            r'amd.*ceo.*depart': -0.8,
            r'amd.*cfo.*resign': -0.6,
            r'amd.*executive.*leave': -0.4
        }
        
        total_score = 0.0
        matches = 0
        
        for pattern, score in event_scores.items():
            if re.search(pattern, text):
                total_score += score
                matches += 1
        
        # Average the scores if multiple events detected
        return total_score / max(matches, 1) if matches > 0 else 0.0
    
    def _calculate_recency_weight(self, timestamp) -> float:
        """Calculate weight based on news recency (recent news weighted higher)"""
        if not timestamp:
            return 0.7  # Default weight for unknown timestamp
        
        try:
            # If timestamp is string, try to parse it
            if isinstance(timestamp, str):
                news_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                news_time = timestamp
            
            hours_old = (datetime.now(news_time.tzinfo) - news_time).total_seconds() / 3600
            
            # Exponential decay: recent news weighted higher
            if hours_old <= 1:
                return 1.0
            elif hours_old <= 6:
                return 0.9
            elif hours_old <= 24:
                return 0.8
            elif hours_old <= 72:
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.7  # Default weight if parsing fails
    
    def _calculate_confidence(self, text: str, lexicon_score: float, 
                            context_score: float, domain_score: float, 
                            amd_score: float, source_weight: float) -> float:
        """Calculate confidence score based on multiple analysis factors"""
        
        # Base confidence from score consistency
        scores = [lexicon_score, context_score, domain_score, amd_score]
        score_variance = np.var([s for s in scores if s != 0.0])
        consistency_confidence = max(0.3, 1.0 - (score_variance * 2))
        
        # Text length confidence (longer texts generally more reliable)
        word_count = len(text.split())
        length_confidence = min(1.0, word_count / 50.0)  # Max confidence at 50+ words
        
        # Source reliability
        source_confidence = source_weight
        
        # Financial term density (more financial terms = higher confidence)
        financial_terms = sum(1 for word in text.split() if word in self.financial_sentiment_lexicon)
        term_density = min(1.0, financial_terms / max(word_count, 1) * 10)
        
        # Weighted average confidence
        confidence = (
            consistency_confidence * 0.3 +
            length_confidence * 0.2 +
            source_confidence * 0.3 +
            term_density * 0.2
        )
        
        return np.clip(confidence, 0.0, 1.0)
    
    def _calculate_weighted_sentiment(self, sentiment_analyses: List[Dict]) -> Dict:
        """Calculate overall weighted sentiment from all analyses"""
        
        if not sentiment_analyses:
            return self._get_fallback_sentiment("No valid sentiment analyses")
        
        # Weight by confidence scores
        weighted_scores = []
        total_confidence = 0.0
        
        for analysis in sentiment_analyses:
            score = analysis['sentiment_score']
            confidence = analysis['confidence']
            weighted_scores.append(score * confidence)
            total_confidence += confidence
        
        # Calculate weighted average
        if total_confidence > 0:
            overall_score = sum(weighted_scores) / total_confidence
        else:
            overall_score = np.mean([a['sentiment_score'] for a in sentiment_analyses])
        
        # Determine direction and confidence
        avg_confidence = np.mean([a['confidence'] for a in sentiment_analyses])
        
        if overall_score > 0.2:
            direction = 'BULLISH'
        elif overall_score < -0.2:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        return {
            'overall_score': overall_score,
            'overall_direction': direction,
            'average_confidence': avg_confidence,
            'analysis_method': 'ADVANCED_NLP',
            'data_quality': 'HIGH' if avg_confidence > 0.7 else 'MEDIUM' if avg_confidence > 0.5 else 'LOW'
        }
    
    def _generate_reasoning(self, lexicon_score: float, context_score: float, 
                          domain_score: float, amd_score: float) -> str:
        """Generate human-readable reasoning for sentiment score"""
        
        components = []
        
        if abs(lexicon_score) > 0.1:
            components.append(f"Lexicon sentiment: {lexicon_score:+.2f}")
        
        if abs(context_score - lexicon_score) > 0.05:
            components.append(f"Context adjustment: {context_score - lexicon_score:+.2f}")
        
        if abs(domain_score - context_score) > 0.05:
            components.append(f"Financial domain: {domain_score - context_score:+.2f}")
        
        if abs(amd_score) > 0.1:
            components.append(f"AMD-specific events: {amd_score:+.2f}")
        
        return "; ".join(components) if components else "Neutral content"
    
    # News source methods
    def _fetch_yahoo_finance_news(self) -> List[Dict]:
        """Fetch news from Yahoo Finance API"""
        try:
            ticker = yf.Ticker(self.symbol)
            news_items = ticker.get_news()
            
            processed_news = []
            for item in news_items[:20]:  # Limit to 20 items
                processed_news.append({
                    'title': item.get('title', ''),
                    'content': item.get('content', ''),
                    'summary': item.get('summary', ''),
                    'timestamp': item.get('providerPublishTime'),
                    'source': 'Yahoo Finance'
                })
            
            return processed_news
            
        except Exception as e:
            print(f"Yahoo Finance fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_marketwatch_rss(self) -> List[Dict]:
        """Fetch news from MarketWatch RSS feeds"""
        try:
            import requests
            from xml.etree import ElementTree as ET
            
            # MarketWatch RSS feeds for financial news
            rss_urls = [
                'https://feeds.marketwatch.com/marketwatch/realtimeheadlines/',
                'https://feeds.marketwatch.com/marketwatch/topstories/'
            ]
            
            processed_news = []
            for url in rss_urls:
                try:
                    response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        root = ET.fromstring(response.content)
                        
                        for item in root.findall('.//item')[:10]:  # Limit to 10 per feed
                            title = item.find('title')
                            description = item.find('description')
                            pub_date = item.find('pubDate')
                            
                            if title is not None and description is not None:
                                # More inclusive filtering for AMD-related news
                                text_content = f"{title.text} {description.text}".lower()
                                if any(keyword in text_content for keyword in ['amd', 'semiconductor', 'chip', 'tech', 'stock', 'market', 'earnings', 'processor', 'gpu', 'cpu']):
                                    processed_news.append({
                                        'title': title.text or '',
                                        'content': description.text or '',
                                        'summary': description.text or '',
                                        'timestamp': pub_date.text if pub_date is not None else None,
                                        'source': 'MarketWatch RSS'
                                    })
                except Exception as e:
                    print(f"MarketWatch RSS individual feed error: {str(e)[:30]}")
                    continue
            
            return processed_news
            
        except Exception as e:
            print(f"MarketWatch RSS fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_seeking_alpha_rss(self) -> List[Dict]:
        """Fetch news from Seeking Alpha RSS"""
        try:
            import requests
            from xml.etree import ElementTree as ET
            
            # Seeking Alpha market news RSS for AMD
            url = 'https://seekingalpha.com/api/sa/combined/AMD.xml'
            
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            processed_news = []
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                for item in root.findall('.//item')[:15]:
                    title = item.find('title')
                    description = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    if title is not None:
                        # More inclusive filtering for relevant content
                        text_content = f"{title.text}".lower()
                        if any(keyword in text_content for keyword in ['amd', 'semiconductor', 'chip', 'tech', 'earnings', 'processor', 'gpu', 'cpu', 'ai']):
                            processed_news.append({
                                'title': title.text or '',
                                'content': description.text if description is not None else '',
                                'summary': description.text if description is not None else title.text or '',
                                'timestamp': pub_date.text if pub_date is not None else None,
                                'source': 'Seeking Alpha RSS'
                            })
            
            return processed_news
            
        except Exception as e:
            print(f"Seeking Alpha RSS fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_ft_rss(self) -> List[Dict]:
        """Fetch news from Financial Times RSS"""
        try:
            import requests
            from xml.etree import ElementTree as ET
            
            # Financial Times Companies RSS
            url = 'https://www.ft.com/companies?format=rss'
            
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            processed_news = []
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                for item in root.findall('.//item')[:10]:
                    title = item.find('title')
                    description = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    if title is not None:
                        # More inclusive filtering for semiconductor/tech related content
                        text_content = f"{title.text}".lower()
                        if any(keyword in text_content for keyword in ['amd', 'semiconductor', 'chip', 'technology', 'ai', 'processor', 'gpu', 'cpu', 'earnings', 'stock']):
                            processed_news.append({
                                'title': title.text or '',
                                'content': description.text if description is not None else '',
                                'summary': description.text if description is not None else title.text or '',
                                'timestamp': pub_date.text if pub_date is not None else None,
                                'source': 'Financial Times RSS'
                            })
            
            return processed_news
            
        except Exception as e:
            print(f"Financial Times RSS fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_reuters_rss(self) -> List[Dict]:
        """Fetch news from Reuters Business RSS"""
        try:
            import requests
            from xml.etree import ElementTree as ET
            
            # Reuters Business and Technology RSS feeds
            rss_urls = [
                'https://feeds.reuters.com/reuters/businessNews',
                'https://feeds.reuters.com/reuters/technologyNews'
            ]
            
            processed_news = []
            for url in rss_urls:
                try:
                    response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        root = ET.fromstring(response.content)
                        
                        for item in root.findall('.//item')[:8]:
                            title = item.find('title')
                            description = item.find('description')
                            pub_date = item.find('pubDate')
                            
                            if title is not None:
                                # Filter for relevant content
                                text_content = f"{title.text} {description.text if description is not None else ''}".lower()
                                if any(keyword in text_content for keyword in ['amd', 'semiconductor', 'chip', 'processor']):
                                    processed_news.append({
                                        'title': title.text or '',
                                        'content': description.text if description is not None else '',
                                        'summary': description.text if description is not None else title.text or '',
                                        'timestamp': pub_date.text if pub_date is not None else None,
                                        'source': 'Reuters Business RSS'
                                    })
                except Exception as e:
                    print(f"Reuters individual feed error: {str(e)[:30]}")
                    continue
            
            return processed_news
            
        except Exception as e:
            print(f"Reuters RSS fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_bloomberg_rss(self) -> List[Dict]:
        """Fetch news from Bloomberg RSS"""
        try:
            import requests
            from xml.etree import ElementTree as ET
            
            # Bloomberg Technology RSS
            url = 'https://feeds.bloomberg.com/technology/news.rss'
            
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            processed_news = []
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                for item in root.findall('.//item')[:10]:
                    title = item.find('title')
                    description = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    if title is not None:
                        # Filter for semiconductor/tech content
                        text_content = f"{title.text}".lower()
                        if any(keyword in text_content for keyword in ['amd', 'semiconductor', 'chip', 'ai', 'processor']):
                            processed_news.append({
                                'title': title.text or '',
                                'content': description.text if description is not None else '',
                                'summary': description.text if description is not None else title.text or '',
                                'timestamp': pub_date.text if pub_date is not None else None,
                                'source': 'Bloomberg RSS'
                            })
            
            return processed_news
            
        except Exception as e:
            print(f"Bloomberg RSS fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_cnbc_rss(self) -> List[Dict]:
        """Fetch news from CNBC RSS"""
        try:
            import requests
            from xml.etree import ElementTree as ET
            
            # CNBC Technology and Business RSS feeds
            rss_urls = [
                'https://feeds.nbcnews.com/nbcnews/public/tech',
                'https://feeds.nbcnews.com/nbcnews/public/business'
            ]
            
            processed_news = []
            for url in rss_urls:
                try:
                    response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        root = ET.fromstring(response.content)
                        
                        for item in root.findall('.//item')[:8]:
                            title = item.find('title')
                            description = item.find('description')
                            pub_date = item.find('pubDate')
                            
                            if title is not None:
                                # Filter for relevant content
                                text_content = f"{title.text}".lower()
                                if any(keyword in text_content for keyword in ['amd', 'semiconductor', 'chip', 'tech earnings']):
                                    processed_news.append({
                                        'title': title.text or '',
                                        'content': description.text if description is not None else '',
                                        'summary': description.text if description is not None else title.text or '',
                                        'timestamp': pub_date.text if pub_date is not None else None,
                                        'source': 'CNBC RSS'
                                    })
                except Exception as e:
                    print(f"CNBC individual feed error: {str(e)[:30]}")
                    continue
            
            return processed_news
            
        except Exception as e:
            print(f"CNBC RSS fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_alpha_vantage_news(self) -> List[Dict]:
        """Fetch news from Alpha Vantage (if API key available)"""
        try:
            import os
            api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
            if not api_key:
                return []
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': self.symbol,
                'apikey': api_key,
                'limit': 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            processed_news = []
            if 'feed' in data:
                for item in data['feed'][:20]:
                    processed_news.append({
                        'title': item.get('title', ''),
                        'content': item.get('summary', ''),
                        'summary': item.get('summary', ''),
                        'timestamp': item.get('time_published'),
                        'source': 'Alpha Vantage'
                    })
            
            return processed_news
            
        except Exception as e:
            print(f"Alpha Vantage fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_financial_news_api(self) -> List[Dict]:
        """Fetch news from Financial News API (placeholder for additional sources)"""
        try:
            # This would integrate with additional financial news APIs
            # For now, return empty list as placeholder
            return []
            
        except Exception as e:
            print(f"Financial News API fetch error: {str(e)[:50]}")
            return []
    
    def _fetch_market_data_news(self) -> List[Dict]:
        """Fetch news from market data providers (placeholder)"""
        try:
            # This would integrate with market data news feeds
            # For now, return empty list as placeholder
            return []
            
        except Exception as e:
            print(f"Market Data News fetch error: {str(e)[:50]}")
            return []
    
    def _get_fallback_sentiment(self, reason: str) -> Dict:
        """Provide fallback neutral sentiment with error information"""
        return {
            'overall_score': 0.0,
            'overall_direction': 'NEUTRAL',
            'average_confidence': 0.0,
            'analysis_method': 'FALLBACK',
            'data_quality': 'FAILED',
            'error_reason': reason,
            'source_breakdown': {},
            'total_articles_analyzed': 0
        }

# Integration function for the existing system
def get_enhanced_sentiment_analysis(symbol="AMD") -> Dict:
    """
    Main entry point for enhanced sentiment analysis
    Returns advanced sentiment analysis to replace basic keyword matching
    """
    analyzer = AdvancedSentimentAnalyzer(symbol)
    return analyzer.analyze_advanced_sentiment()

if __name__ == "__main__":
    # Test the enhanced sentiment analyzer
    result = get_enhanced_sentiment_analysis("AMD")
    print(json.dumps(result, indent=2))