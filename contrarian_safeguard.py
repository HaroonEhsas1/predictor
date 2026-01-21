"""Contrarian safeguard: flips strategy when rolling accuracy drops below 40%.

Prevents getting stuck in losing streaks by inverting predictions.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

HISTORY_FILE = Path(__file__).parent / "data" / "prediction_history.json"
HISTORY_FILE.parent.mkdir(exist_ok=True)

class ContrarianSafeguard:
    """Tracks rolling win-rate and inverts strategy when needed."""
    
    def __init__(self, window_size=20, flip_threshold=0.40):
        self.window_size = window_size
        self.flip_threshold = flip_threshold
        self.history = self._load_history()
        
    def _load_history(self) -> List[Dict]:
        """Load prediction history from disk."""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save history to disk."""
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def log_prediction(self, prediction: str, actual: Optional[str] = None):
        """Log a new prediction (and outcome if known)."""
        entry = {
            'date': datetime.now().isoformat(),
            'predicted': prediction,
            'actual': actual,
            'correct': prediction == actual if actual else None
        }
        self.history.append(entry)
        self._save_history()
    
    def update_outcome(self, date_str: str, actual: str):
        """Update the actual outcome for a past prediction."""
        for entry in reversed(self.history):
            if entry['date'].startswith(date_str):
                entry['actual'] = actual
                entry['correct'] = (entry['predicted'] == actual)
                self._save_history()
                return
    
    def get_rolling_accuracy(self) -> float:
        """Calculate accuracy over last N predictions."""
        recent = [e for e in self.history if e['correct'] is not None][-self.window_size:]
        if not recent:
            return 0.50  # Neutral
        correct = sum(e['correct'] for e in recent)
        return correct / len(recent)
    
    def should_flip(self) -> bool:
        """Check if strategy should be inverted."""
        acc = self.get_rolling_accuracy()
        return acc < self.flip_threshold
    
    def apply_safeguard(self, prediction: Dict) -> Dict:
        """Apply contrarian flip if needed."""
        if self.should_flip():
            original = prediction['direction']
            flipped = 'DOWN' if original == 'UP' else 'UP'
            acc = self.get_rolling_accuracy()
            
            prediction['direction'] = flipped
            prediction['contrarian_flip'] = True
            prediction['rolling_accuracy'] = acc
            prediction['reason'] = f"⚠️ CONTRARIAN FLIP: Rolling accuracy {acc:.1%} < {self.flip_threshold:.0%}"
            
            print(f"🔄 CONTRARIAN FLIP ACTIVATED!")
            print(f"   Original: {original} → Flipped: {flipped}")
            print(f"   Reason: Accuracy {acc:.1%} over last {self.window_size} trades")
        else:
            prediction['contrarian_flip'] = False
            prediction['rolling_accuracy'] = self.get_rolling_accuracy()
        
        return prediction
    
    def get_status(self) -> Dict:
        """Get current safeguard status."""
        acc = self.get_rolling_accuracy()
        total_predictions = len([e for e in self.history if e['correct'] is not None])
        
        return {
            'rolling_accuracy': acc,
            'flip_active': acc < self.flip_threshold,
            'total_predictions': total_predictions,
            'window_size': self.window_size,
            'flip_threshold': self.flip_threshold
        }

# Global instance
safeguard = ContrarianSafeguard()

if __name__ == "__main__":
    print("📊 Contrarian Safeguard Status:")
    status = safeguard.get_status()
    print(f"   Rolling Accuracy: {status['rolling_accuracy']:.1%}")
    print(f"   Flip Active: {status['flip_active']}")
    print(f"   Total Predictions: {status['total_predictions']}")
