"""
AVGO (Broadcom) CATALYST DETECTOR
==================================
Detects AVGO-specific business catalysts that drive stock movement
Focuses on M&A, VMware, semiconductors, networking, iPhone design wins

Author: StockSense System
Created: Oct 27, 2025
"""

import re
from typing import Dict, List, Tuple

class BroadcomCatalystDetector:
    """
    Detects AVGO-specific catalysts from news and announcements
    """
    
    def __init__(self):
        """Initialize catalyst categories and keywords"""
        
        # Define catalyst categories with impact weights
        self.catalyst_categories = {
            'ma_activity': {
                'weight': 0.20,  # HIGHEST - biggest stock mover
                'keywords': [
                    'acquisition', 'merger', 'acquires', 'buyout',
                    'strategic acquisition', 'deal', 'm&a', 'purchases',
                    'broadcom acquires', 'broadcom buys', 'takeover',
                    'consolidation'
                ],
                'impact': 'VERY_POSITIVE'
            },
            
            'vmware_synergies': {
                'weight': 0.15,  # VERY HIGH - recent major acquisition
                'keywords': [
                    'vmware', 'vmware integration', 'vmware revenue',
                    'vmware synergy', 'multi-cloud', 'hybrid cloud',
                    'virtualization', 'vcf', 'vmware cloud foundation',
                    'tanzu', 'vmware deals'
                ],
                'impact': 'VERY_POSITIVE'
            },
            
            'semiconductor_demand': {
                'weight': 0.12,  # HIGH - core business
                'keywords': [
                    'chip demand', 'semiconductor orders', 'foundry capacity',
                    'ai chips', 'networking chips', 'custom silicon',
                    'asic', 'custom chip design', 'silicon revenue'
                ],
                'impact': 'POSITIVE'
            },
            
            'iphone_design_wins': {
                'weight': 0.12,  # HIGH - Apple relationship
                'keywords': [
                    'apple', 'iphone', 'apple partnership', 'design win apple',
                    'apple chip', 'fbar', 'rf component', 'wireless chip',
                    'apple supply', 'iphone 16', 'iphone 17'
                ],
                'impact': 'VERY_POSITIVE'
            },
            
            'networking_infrastructure': {
                'weight': 0.10,  # HIGH - growth area
                'keywords': [
                    'data center networking', 'ethernet switch',
                    'tomahawk', 'jericho', 'trident', '400g', '800g',
                    'networking silicon', 'switch chip', 'ai networking',
                    'ultra ethernet'
                ],
                'impact': 'POSITIVE'
            },
            
            'ai_infrastructure': {
                'weight': 0.10,  # HIGH - emerging growth
                'keywords': [
                    'ai infrastructure', 'ai data center', 'ai networking',
                    'nvidia partnership', 'gpu interconnect', 'xpu',
                    'ai accelerator', 'inference chip'
                ],
                'impact': 'POSITIVE'
            },
            
            'enterprise_software': {
                'weight': 0.08,  # MEDIUM - post-VMware
                'keywords': [
                    'enterprise software', 'software revenue',
                    'subscription growth', 'saas', 'infrastructure software',
                    'software transition', 'recurring revenue'
                ],
                'impact': 'POSITIVE'
            },
            
            'wireless_5g': {
                'weight': 0.08,  # MEDIUM
                'keywords': [
                    '5g', '5g deployment', 'wireless infrastructure',
                    'base station', 'small cell', '5g chip',
                    'wireless revenue', 'carrier spending'
                ],
                'impact': 'POSITIVE'
            },
            
            'optical_fiber': {
                'weight': 0.06,  # MEDIUM-LOW
                'keywords': [
                    'optical', 'fiber optic', 'coherent optics',
                    '400g optics', '800g optics', 'silicon photonics',
                    'data center interconnect'
                ],
                'impact': 'POSITIVE'
            },
            
            # Negative catalysts
            'regulatory_concerns': {
                'weight': -0.12,  # Negative
                'keywords': [
                    'antitrust', 'ftc', 'regulatory approval',
                    'competition concern', 'monopoly', 'doj investigation',
                    'vmware deal delay', 'regulatory hurdle'
                ],
                'impact': 'NEGATIVE'
            },
            
            'customer_concentration': {
                'weight': -0.08,  # Negative
                'keywords': [
                    'apple reduces orders', 'apple diversification',
                    'customer concentration risk', 'apple dependency',
                    'single customer risk', 'apple alternatives'
                ],
                'impact': 'NEGATIVE'
            },
            
            'integration_challenges': {
                'weight': -0.10,  # Negative
                'keywords': [
                    'integration issues', 'vmware integration delay',
                    'merger challenges', 'restructuring costs',
                    'integration expenses', 'synergy delay'
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
            return "No significant AVGO-specific catalysts detected"
        
        lines = []
        lines.append(f"📊 AVGO-Specific Catalysts Detected: {catalyst_result['total_catalysts']}")
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
    detector = BroadcomCatalystDetector()
    
    print("="*80)
    print("🧪 AVGO CATALYST DETECTOR - TEST")
    print("="*80)
    
    test_cases = [
        {
            'name': 'M&A Activity',
            'news': [
                "Broadcom in talks to acquire enterprise software company",
                "AVGO announces strategic acquisition in networking space"
            ]
        },
        {
            'name': 'VMware Synergies',
            'news': [
                "Broadcom-VMware integration ahead of schedule",
                "VMware cloud revenue exceeds expectations",
                "Multi-cloud deals surge after Broadcom acquisition"
            ]
        },
        {
            'name': 'iPhone Design Win',
            'news': [
                "Apple selects Broadcom chips for iPhone 16",
                "AVGO RF components win in next-gen iPhone",
                "Apple partnership extends through 2027"
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
            print("✅ STRONG POSITIVE catalyst - boost AVGO prediction")
        elif result['score'] > 0.06:
            print("✅ POSITIVE catalyst - modest boost")
        else:
            print("➡️ NEUTRAL - no significant catalyst impact")
    
    print(f"\n{'='*80}")
    print("✅ AVGO CATALYST DETECTOR READY")
    print("="*80)
