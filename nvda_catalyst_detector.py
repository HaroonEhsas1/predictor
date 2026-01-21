"""
NVDA CATALYST DETECTOR
======================
Detects NVIDIA-specific business catalysts that drive stock movement
Focuses on AI chips, data center, gaming GPUs, partnerships, product launches

Author: StockSense System
Created: Nov 12, 2025
"""

import re
from typing import Dict, List, Tuple


class NVDACatalystDetector:
    """
    Detects NVIDIA-specific catalysts from news and announcements
    """

    def __init__(self):
        """Initialize catalyst categories and keywords"""

        # Define catalyst categories with impact weights
        self.catalyst_categories = {
            'ai_chip_demand': {
                'weight': 0.20,  # VERY HIGH - biggest growth driver
                'keywords': [
                    'h100', 'h200', 'blackwell', 'hopper', 'a100', 'a800',
                    'ai chip demand', 'gpu shortage', 'data center ai',
                    'ai infrastructure', 'ai training', 'llm training',
                    'chatgpt', 'openai', 'anthropic', 'ai boom',
                    'insatiable demand', 'ai chip backlog', 'order backlog'
                ],
                'impact': 'VERY_POSITIVE'
            },

            'data_center_wins': {
                'weight': 0.18,  # VERY HIGH - major revenue driver
                'keywords': [
                    'data center win', 'cloud partnership', 'aws nvidia',
                    'azure nvidia', 'google cloud nvidia', 'meta nvidia',
                    'oracle nvidia', 'supercomputer', 'ai supercomputer',
                    'data center expansion', 'hyperscaler', 'enterprise ai'
                ],
                'impact': 'VERY_POSITIVE'
            },

            'product_launches': {
                'weight': 0.15,  # HIGH - drives stock momentum
                'keywords': [
                    'rtx 50', 'rtx 5090', 'rtx 5080', 'blackwell gpu',
                    'new gpu launch', 'next gen', 'ada lovelace',
                    'geforce rtx', 'gpu announcement', 'product launch'
                ],
                'impact': 'VERY_POSITIVE'
            },

            'gaming_gpu': {
                'weight': 0.12,  # HIGH - core business
                'keywords': [
                    'gaming gpu', 'geforce', 'rtx', 'dlss', 'ray tracing',
                    'gpu market share', 'gaming market', 'esports',
                    'gaming performance', 'gpu sales', 'graphics card'
                ],
                'impact': 'POSITIVE'
            },

            'automotive_partnerships': {
                'weight': 0.10,  # HIGH - growth area
                'keywords': [
                    'automotive', 'self-driving', 'autonomous vehicle',
                    'tesla nvidia', 'drive agx', 'orin', 'automotive ai',
                    'adas', 'automotive partnership', 'car ai'
                ],
                'impact': 'POSITIVE'
            },

            'enterprise_ai': {
                'weight': 0.12,  # HIGH - enterprise adoption
                'keywords': [
                    'enterprise ai', 'ai enterprise', 'nvidia ai enterprise',
                    'dgx', 'dgx cloud', 'ai platform', 'enterprise deployment',
                    'ai software', 'nvidia omniverse', 'enterprise partnership'
                ],
                'impact': 'POSITIVE'
            },

            'cuda_ecosystem': {
                'weight': 0.08,  # MEDIUM - competitive moat
                'keywords': [
                    'cuda', 'cuda advantage', 'cuda ecosystem',
                    'developer adoption', 'ai framework', 'pytorch',
                    'tensorflow', 'ai development', 'developer tools'
                ],
                'impact': 'POSITIVE'
            },

            'china_restrictions': {
                'weight': -0.15,  # NEGATIVE - major risk
                'keywords': [
                    'china ban', 'export restrictions', 'china restrictions',
                    'us export ban', 'china market loss', 'trade restrictions',
                    'geopolitical risk', 'china revenue', 'export controls'
                ],
                'impact': 'VERY_NEGATIVE'
            },

            'competition_concerns': {
                'weight': -0.10,  # NEGATIVE
                'keywords': [
                    'amd competition', 'intel gpu', 'custom silicon',
                    'google tpu', 'amazon trainium', 'microsoft maia',
                    'market share loss', 'competition threat', 'alternative ai chip'
                ],
                'impact': 'NEGATIVE'
            },

            'supply_constraints': {
                'weight': -0.08,  # NEGATIVE
                'keywords': [
                    'supply shortage', 'chip shortage', 'production delay',
                    'tsmc capacity', 'supply chain issue', 'manufacturing delay',
                    'yield issues', 'supply constraint'
                ],
                'impact': 'NEGATIVE'
            },

            'guidance_beat': {
                'weight': 0.12,  # HIGH - earnings catalyst
                'keywords': [
                    'beats expectations', 'raises guidance', 'strong guidance',
                    'outlook raised', 'guidance increase', 'earnings beat',
                    'revenue beat', 'guidance upgrade'
                ],
                'impact': 'VERY_POSITIVE'
            },

            'guidance_miss': {
                'weight': -0.12,  # NEGATIVE - earnings risk
                'keywords': [
                    'misses expectations', 'lowers guidance', 'weak guidance',
                    'outlook lowered', 'guidance cut', 'earnings miss',
                    'revenue miss', 'guidance downgrade'
                ],
                'impact': 'VERY_NEGATIVE'
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
        if total_score > 0.20:
            sentiment = 'VERY_POSITIVE'
        elif total_score > 0.10:
            sentiment = 'POSITIVE'
        elif total_score < -0.20:
            sentiment = 'VERY_NEGATIVE'
        elif total_score < -0.10:
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
            return "No significant NVIDIA-specific catalysts detected"

        lines = []
        lines.append(
            f"📊 NVIDIA-Specific Catalysts Detected: {catalyst_result['total_catalysts']}")
        lines.append(f"   Overall Sentiment: {catalyst_result['sentiment']}")
        lines.append(f"   Catalyst Score: {catalyst_result['score']:+.3f}")

        if catalyst_result['top_catalysts']:
            lines.append(f"\n   Top Catalysts:")
            for cat in catalyst_result['top_catalysts']:
                impact_emoji = "📈" if cat['score'] > 0 else "📉"
                lines.append(
                    f"   {impact_emoji} {cat['category']}: {cat['score']:+.3f}")
                lines.append(
                    f"      Matched: {', '.join(cat['keywords_matched'])}")

        return '\n'.join(lines)


if __name__ == "__main__":
    # Test the catalyst detector
    detector = NVDACatalystDetector()

    print("="*80)
    print("🧪 NVIDIA CATALYST DETECTOR - TEST")
    print("="*80)

    test_cases = [
        {
            'name': 'AI Chip Demand Surge',
            'news': [
                "NVIDIA H100 GPU demand insatiable, backlog extends to 6 months",
                "OpenAI expands NVIDIA GPU infrastructure for ChatGPT training",
                "Meta increases NVIDIA AI chip orders for AI research"
            ]
        },
        {
            'name': 'Data Center Win',
            'news': [
                "AWS announces major NVIDIA partnership for AI infrastructure",
                "Microsoft Azure expands NVIDIA GPU instances",
                "Google Cloud deploys NVIDIA Blackwell supercomputers"
            ]
        },
        {
            'name': 'Product Launch',
            'news': [
                "NVIDIA announces RTX 5090 gaming GPU with advanced AI features",
                "Blackwell GPU architecture delivers 2x performance",
                "NVIDIA launches next-gen AI chips for data centers"
            ]
        },
        {
            'name': 'China Restrictions',
            'news': [
                "US tightens export restrictions on NVIDIA chips to China",
                "NVIDIA faces revenue loss from China market restrictions",
                "Geopolitical tensions impact NVIDIA China sales"
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

        if result['score'] > 0.15:
            print("✅ STRONG POSITIVE catalyst - boost NVDA prediction")
        elif result['score'] > 0.08:
            print("✅ POSITIVE catalyst - modest boost")
        elif result['score'] < -0.15:
            print("❌ STRONG NEGATIVE catalyst - reduce NVDA prediction")
        elif result['score'] < -0.08:
            print("⚠️ NEGATIVE catalyst - modest penalty")
        else:
            print("➡️ NEUTRAL - no significant catalyst impact")

    print(f"\n{'='*80}")
    print("✅ NVIDIA CATALYST DETECTOR READY")
    print("="*80)
