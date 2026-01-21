"""
Configuration for Next-Day Prediction Engine
Professional trading system with institutional-grade safety controls
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class NextDayConfig:
    """Configuration for next-day prediction engine"""
    
    # Safety controls (institutional grade)
    enabled: bool = False  # Feature flag - disabled by default
    dry_run: bool = True   # Always dry run by default
    
    # Contrarian Analysis Configuration
    enable_contrarian_signals: bool = False  # Enable advanced contrarian analysis (disabled by default)
    
    # Confidence gating thresholds
    min_confidence: float = 0.80      # Minimum calibrated probability
    min_ensemble_consensus: float = 0.80  # Minimum ensemble agreement
    min_gap_threshold: float = 0.005  # Minimum gap magnitude (0.5%) for institutional relevance
    
    # Model artifacts paths
    models_path: str = "./models/nextday"
    data_path: str = "./data/nextday"
    
    # Data validation
    max_missing_data_pct: float = 0.05  # 5% max missing data tolerance
    required_lookback_days: int = 20    # Minimum historical data required (reduced for demo)
    
    # Feature engineering
    volatility_windows: Optional[list] = None
    futures_weight_halflife: int = 5    # Days for volatility weighting
    
    # Risk management
    max_position_size: float = 0.02     # 2% max position size
    stop_loss_pct: float = 0.03         # 3% stop loss
    
    # Position sizing parameters
    gap_size_multiplier: float = 10.0   # Multiplier for gap magnitude in position sizing
    max_gap_multiplier: float = 2.0     # Maximum gap multiplier cap
    min_position_size: float = 0.001    # Minimum position size
    
    # Model training
    train_test_split: float = 0.8
    cv_folds: int = 5
    purge_days: int = 2                 # Purge 2 days to prevent leakage
    
    def __post_init__(self):
        if self.volatility_windows is None:
            self.volatility_windows = [5, 10, 20]
        
        # Ensure directories exist
        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)

# Global configuration instance
CONFIG = NextDayConfig()

def update_config(updates: Dict[str, Any]) -> None:
    """Update configuration with new values"""
    for key, value in updates.items():
        if hasattr(CONFIG, key):
            setattr(CONFIG, key, value)
        else:
            raise ValueError(f"Invalid config key: {key}")

def get_model_version() -> str:
    """Generate versioned model name"""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d")