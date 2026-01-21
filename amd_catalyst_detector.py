"""
AMD CATALYST DETECTOR
=====================
Detects AMD-specific business catalysts that drive stock movement
Focuses on gaming GPUs, data center, AI accelerators, CPU market share

Author: StockSense System
Created: Oct 27, 2025
"""

import re
from typing import Dict, List, Tuple

class AMDCatalystDetector:
    """
    Detects AMD-specific catalysts from news and announcements
    """
    
    def __init__(self):
        """Initialize catalyst categories and keywords"""
        
        # Define catalyst categories with impact weights
        self.catalyst_categories = {
            'datacenter_ai_wins': {
                'weight': 0.18,  # VERY HIGH - biggest growth driver
                'keywords': [
                    'epyc', 'mi300', 'mi250', 'instinct', 'data center win',
                    'server market share', 'amd instinct', 'genoa', 'bergamo',
                    'ai accelerator', 'gpu compute', 'supercomputer',
                    'azure amd', 'aws amd', 'google cloud amd', 'meta amd'
                ],
                'impact': 'VERY_POSITIVE'
            },
            
            'gaming_gpu': {
                'weight': 0.12,  # HIGH - core business
                'keywords': [
                    'radeon', 'rdna', 'rx 7900', 'rx 7800', 'gaming gpu',
                    'graphics card', 'gpu market share', 'amd advantage',
                    'fsr', 'fidelity super resolution', 'console gaming'
                ],
                'impact': 'POSITIVE'
            },
            
            'cpu_market_share': {
                'weight': 0.15,  # VERY HIGH - Intel competition
                'keywords': [
                    'ryzen', 'threadripper', 'cpu market share',
                    'beats intel', 'intel market share loss',
                    'desktop market share', 'laptop market share',
                    'x3d', 'zen 5', 'zen 4'
                ],
                'impact': 'VERY_POSITIVE'
            },
            
            'console_partnerships': {
                'weight': 0.08,  # MEDIUM - steady revenue
                'keywords': [
                    'playstation', 'ps5', 'xbox', 'series x',
                    'sony partnership', 'microsoft xbox', 'steam deck',
                    'handheld gaming', 'rog ally'
                ],
                'impact': 'POSITIVE'
            },
            
            'ai_ml_adoption': {
                'weight': 0.12,  # HIGH - future growth
                'keywords': [
                    'ai training', 'machine learning', 'llm training',
                    'generative ai', 'chatgpt amd', 'ai inference',
                    'rocm', 'pytorch amd', 'tensorflow amd',
                    'nvidia alternative', 'cuda alternative'
                ],
                'impact': 'VERY_POSITIVE'
            },
            
            'process_technology': {
                'weight': 0.07,  # MEDIUM - competitive advantage
                'keywords': [
                    '3nm', '5nm', '7nm', 'tsmc partnership',
                    'chiplet design', 'advanced packaging',
                    '3d v-cache', 'node advantage'
                ],
                'impact': 'POSITIVE'
            },
            
            'cloud_partnerships': {
                'weight': 0.10,  # HIGH - major revenue
                'keywords': [
                    'microsoft azure', 'aws partnership', 'google cloud partnership',
                    'oracle cloud', 'alibaba cloud', 'tencent cloud',
                    'cloud instance', 'cloud adoption'
                ],
                'impact': 'POSITIVE'
            },
            
            'automotive_embedded': {
                'weight': 0.06,  # MEDIUM-LOW - growth area
                'keywords': [
                    'tesla amd', 'automotive', 'adas', 'self-driving',
                    'embedded', 'industrial', 'automotive compute'
                ],
                'impact': 'POSITIVE'
            },
            
            # Negative catalysts
            'gpu_competition': {
                'weight': -0.10,  # Negative
                'keywords': [
                    'nvidia wins', 'loses to nvidia', 'rtx superior',
                    'cuda advantage', 'market share loss gpu',
                    'intel arc', 'gpu underperforming'
                ],
                'impact': 'NEGATIVE'
            },
            
            'supply_constraints': {
                'weight': -0.08,  # Negative
                'keywords': [
                    'chip shortage', 'wafer shortage', 'tsmc allocation',
                    'supply chain issue', 'production delay',
                    'yield issues', 'shortage impact'
                ],
                'impact': 'NEGATIVE'
            },
            
            'competitive_losses': {
                'weight': -0.12,  # Negative
                'keywords': [
                    'loses to intel', 'intel regains share',
                    'dell chooses intel', 'hp intel',
                    'oem prefers intel', 'server loss'
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
        if total_score > 0.15:
            sentiment = 'VERY_POSITIVE'
        elif total_score > 0.08:
            sentiment = 'POSITIVE'
        elif total_score < -0.15:
            sentiment = 'VERY_NEGATIVE'
        elif total_score < -0.08:
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
            return "No significant AMD-specific catalysts detected"
        
        lines = []
        lines.append(f"📊 AMD-Specific Catalysts Detected: {catalyst_result['total_catalysts']}")
        lines.append(f"   Overall Sentiment: {catalyst_result['sentiment']}")
        lines.append(f"   Catalyst Score: {catalyst_result['score']:+.3f}")
        
        if catalyst_result['top_catalysts']:
            lines.append(f"\n   Top Catalysts:")
            for cat in catalyst_result['top_catalysts']:
                impact_emoji = "📈" if cat['score'] > 0 else "📉"
                lines.append(f"   {impact_emoji} {cat['category']}: {cat['score']:+.3f}")
                lines.append(f"      Matched: {', '.join(cat['keywords_matched'])}")
        
        return '\n'.join(lines)


if __name__ == "__main__":
    # Test the catalyst detector
    detector = AMDCatalystDetector()
    
    print("="*80)
    print("🧪 AMD CATALYST DETECTOR - TEST")
    print("="*80)
    
    test_cases = [
        {
            'name': 'Data Center + AI Win',
            'news': [
                "AMD EPYC processors win major cloud contract",
                "AMD Instinct MI300 chosen for AI training by Meta",
                "AWS expands AMD instance offerings"
            ]
        },
        {
            'name': 'CPU Market Share Gain',
            'news': [
                "AMD Ryzen gains desktop market share from Intel",
                "Dell expands AMD laptop lineup",
                "AMD Zen 5 outperforms Intel in benchmarks"
            ]
        },
        {
            'name': 'Gaming GPU Success',
            'news': [
                "AMD Radeon RX 7900 XTX sales surge",
                "FSR 3.0 adoption grows among game developers"
            ]
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"📰 TEST: {test['name']}")
        print(f"{'='*80}")
        
        result = detector.detect_catalysts(test['news'])
        explanation = detector.get_catalyst_explanation(result)
        
        print(f"\n{explanation}")
        print(f"\n📊 Score: {result['score']:+.3f}")
        
        if result['score'] > 0.12:
            print("✅ STRONG POSITIVE catalyst - boost AMD prediction")
        elif result['score'] > 0.06:
            print("✅ POSITIVE catalyst - modest boost")
        else:
            print("➡️ NEUTRAL - no significant catalyst impact")
    
    print(f"\n{'='*80}")
    print("✅ AMD CATALYST DETECTOR READY")
    print("="*80)
