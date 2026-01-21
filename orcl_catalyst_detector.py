"""
ORACLE CATALYST DETECTOR
========================
Detects ORCL-specific business catalysts that drive stock movement
Focuses on enterprise software, cloud, database, and healthcare IT

Author: StockSense System
Created: Oct 27, 2025
"""

import re
from typing import Dict, List, Tuple

class OracleCatalystDetector:
    """
    Detects Oracle-specific catalysts from news and announcements
    """
    
    def __init__(self):
        """Initialize catalyst categories and keywords"""
        
        # Define catalyst categories with impact weights
        self.catalyst_categories = {
            'cloud_wins': {
                'weight': 0.15,  # High impact - core growth driver
                'keywords': [
                    'oracle cloud infrastructure', 'oci', 'cloud infrastructure win',
                    'cloud contract', 'cloud deal', 'cloud migration',
                    'multicloud', 'cloud adoption', 'cloud revenue growth',
                    'cloud acceleration', 'infrastructure-as-a-service', 'iaas'
                ],
                'impact': 'VERY_POSITIVE'
            },
            
            'database_growth': {
                'weight': 0.12,  # High impact - core business
                'keywords': [
                    'autonomous database', 'oracle database', 'exadata',
                    'database subscription', 'database cloud', 'mysql',
                    'oracle database@azure', 'database modernization',
                    'database migration', 'nosql', 'oracle database 23ai'
                ],
                'impact': 'POSITIVE'
            },
            
            'enterprise_wins': {
                'weight': 0.10,  # Medium-high impact
                'keywords': [
                    'enterprise contract', 'large deal', 'fortune 500',
                    'global 2000', 'enterprise win', 'strategic partnership',
                    'multi-year contract', 'billion-dollar deal',
                    'government contract', 'federal contract'
                ],
                'impact': 'POSITIVE'
            },
            
            'cerner_healthcare': {
                'weight': 0.08,  # Medium impact - growth area
                'keywords': [
                    'cerner', 'oracle health', 'healthcare it',
                    'electronic health records', 'ehr', 'hospital system',
                    'healthcare cloud', 'medical records', 'health tech'
                ],
                'impact': 'POSITIVE'
            },
            
            'ai_innovation': {
                'weight': 0.08,  # Medium impact - future growth
                'keywords': [
                    'artificial intelligence', 'generative ai', 'machine learning',
                    'oracle ai', 'ai database', 'ai infrastructure',
                    'gpu cloud', 'nvidia partnership', 'ai workloads',
                    'oracle database 23ai', 'vector database'
                ],
                'impact': 'POSITIVE'
            },
            
            'partnerships': {
                'weight': 0.07,  # Medium impact
                'keywords': [
                    'microsoft azure', 'database@azure', 'google cloud',
                    'aws partnership', 'strategic alliance', 'coopetition',
                    'technology partnership', 'integration partnership'
                ],
                'impact': 'POSITIVE'
            },
            
            'financial_beats': {
                'weight': 0.10,  # High impact
                'keywords': [
                    'beats estimates', 'earnings beat', 'revenue beat',
                    'guidance raise', 'raised guidance', 'strong quarter',
                    'record revenue', 'cloud revenue growth', 'rpd growth',
                    'operating margin expansion'
                ],
                'impact': 'VERY_POSITIVE'
            },
            
            'competitive_wins': {
                'weight': 0.06,  # Medium-low impact
                'keywords': [
                    'wins vs aws', 'wins vs azure', 'market share gain',
                    'competitive advantage', 'displaces competitor',
                    'migration from sap', 'migration from aws'
                ],
                'impact': 'POSITIVE'
            },
            
            # Negative catalysts
            'cloud_losses': {
                'weight': -0.10,  # Negative impact
                'keywords': [
                    'loses to aws', 'loses to azure', 'loses to google',
                    'customer churn', 'migration to aws', 'migration to azure',
                    'competitive pressure', 'market share loss'
                ],
                'impact': 'NEGATIVE'
            },
            
            'legal_regulatory': {
                'weight': -0.08,  # Negative impact
                'keywords': [
                    'lawsuit', 'litigation', 'regulatory investigation',
                    'antitrust', 'compliance issue', 'sec investigation',
                    'privacy violation', 'data breach'
                ],
                'impact': 'NEGATIVE'
            },
            
            'exec_departures': {
                'weight': -0.05,  # Negative impact
                'keywords': [
                    'ceo departure', 'executive departure', 'cto leaves',
                    'key executive exits', 'management change',
                    'leadership transition'
                ],
                'impact': 'NEGATIVE'
            }
        }
    
    def detect_catalysts(self, news_articles: List[str]) -> Dict:
        """
        Detect catalysts from news articles
        
        Args:
            news_articles: List of news article titles/snippets
            
        Returns:
            Dict with catalyst score and details
        """
        if not news_articles:
            return {
                'score': 0.0,
                'catalysts_found': [],
                'total_catalysts': 0,
                'sentiment': 'NEUTRAL'
            }
        
        catalysts_found = []
        total_score = 0.0
        
        # Combine all articles into one text for analysis
        all_text = ' '.join(news_articles).lower()
        
        # Check each catalyst category
        for category, config in self.catalyst_categories.items():
            # Count keyword matches
            matches = []
            for keyword in config['keywords']:
                if keyword.lower() in all_text:
                    matches.append(keyword)
            
            if matches:
                # Calculate score for this category
                # More matches = stronger signal
                match_strength = min(len(matches) / 3.0, 1.0)  # Cap at 1.0
                category_score = config['weight'] * match_strength
                
                total_score += category_score
                
                catalysts_found.append({
                    'category': category,
                    'impact': config['impact'],
                    'score': category_score,
                    'keywords_matched': matches[:3],  # Top 3 matches
                    'match_count': len(matches)
                })
        
        # Determine overall sentiment
        if total_score > 0.10:
            sentiment = 'VERY_POSITIVE'
        elif total_score > 0.05:
            sentiment = 'POSITIVE'
        elif total_score < -0.10:
            sentiment = 'VERY_NEGATIVE'
        elif total_score < -0.05:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'
        
        return {
            'score': total_score,
            'catalysts_found': catalysts_found,
            'total_catalysts': len(catalysts_found),
            'sentiment': sentiment,
            'top_catalysts': sorted(catalysts_found, 
                                   key=lambda x: abs(x['score']), 
                                   reverse=True)[:3]
        }
    
    def get_catalyst_explanation(self, catalyst_result: Dict) -> str:
        """Generate human-readable explanation of catalysts"""
        
        if catalyst_result['total_catalysts'] == 0:
            return "No significant ORCL-specific catalysts detected"
        
        lines = []
        lines.append(f"📊 ORCL-Specific Catalysts Detected: {catalyst_result['total_catalysts']}")
        lines.append(f"   Overall Sentiment: {catalyst_result['sentiment']}")
        lines.append(f"   Catalyst Score: {catalyst_result['score']:+.3f}")
        
        if catalyst_result['top_catalysts']:
            lines.append(f"\n   Top Catalysts:")
            for cat in catalyst_result['top_catalysts']:
                impact_emoji = "📈" if cat['score'] > 0 else "📉"
                lines.append(f"   {impact_emoji} {cat['category']}: {cat['score']:+.3f}")
                lines.append(f"      Matched: {', '.join(cat['keywords_matched'])}")
        
        return '\n'.join(lines)


def test_catalyst_detector():
    """Test the catalyst detector with sample news"""
    
    detector = OracleCatalystDetector()
    
    print("="*80)
    print("🧪 ORACLE CATALYST DETECTOR - TEST")
    print("="*80)
    
    # Test cases
    test_cases = [
        {
            'name': 'Cloud Win',
            'news': [
                "Oracle wins major cloud infrastructure deal with Fortune 500 company",
                "OCI revenue growth accelerates 30% year-over-year"
            ]
        },
        {
            'name': 'Database Growth',
            'news': [
                "Oracle Autonomous Database adoption surges among enterprises",
                "Oracle Database@Azure partnership drives new subscriptions"
            ]
        },
        {
            'name': 'AI Innovation',
            'news': [
                "Oracle launches AI-powered database features with vector search",
                "Oracle partners with NVIDIA for GPU cloud infrastructure",
                "Generative AI workloads choose Oracle Cloud"
            ]
        },
        {
            'name': 'Earnings Beat',
            'news': [
                "Oracle beats earnings estimates on strong cloud revenue",
                "Oracle raises full-year guidance as cloud revenue accelerates"
            ]
        },
        {
            'name': 'Mixed Signals',
            'news': [
                "Oracle wins healthcare contract with Cerner integration",
                "But faces competitive pressure from AWS in government sector"
            ]
        },
        {
            'name': 'Negative News',
            'news': [
                "Oracle loses major contract to AWS",
                "Customer migration to Azure raises concerns"
            ]
        },
        {
            'name': 'No Catalysts',
            'news': [
                "Oracle stock up on market momentum",
                "Tech sector rallies boost Oracle shares"
            ]
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"📰 TEST: {test['name']}")
        print(f"{'='*80}")
        print(f"News: {test['news']}\n")
        
        result = detector.detect_catalysts(test['news'])
        explanation = detector.get_catalyst_explanation(result)
        
        print(explanation)
        print(f"\n📊 Score: {result['score']:+.3f}")
        
        if result['score'] > 0.10:
            print("✅ STRONG POSITIVE catalyst - boost ORCL prediction")
        elif result['score'] > 0.05:
            print("✅ POSITIVE catalyst - modest boost")
        elif result['score'] < -0.10:
            print("❌ STRONG NEGATIVE catalyst - reduce ORCL prediction")
        elif result['score'] < -0.05:
            print("❌ NEGATIVE catalyst - modest reduction")
        else:
            print("➡️ NEUTRAL - no significant catalyst impact")
    
    print(f"\n{'='*80}")
    print("✅ CATALYST DETECTOR TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_catalyst_detector()
