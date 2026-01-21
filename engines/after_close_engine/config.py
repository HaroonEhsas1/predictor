"""
Configuration management for After Close Engine
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration class for After Close Engine"""
    
    # Core engine settings
    after_close_enabled: bool = True
    confidence_threshold: float = 0.70  # Base threshold, dynamically adjusted by get_adaptive_confidence_threshold()
    symbol: str = "AMD"
    
    # Paths
    prediction_path: str = "./data/predictions/after_close"
    log_path: str = "./logs/after_close"  
    model_path: str = "./models"
    sample_data_path: str = "./sample_data"
    snapshot_path: str = "./data/engine_snapshot/latest.json"
    
    # Development settings
    auto_fit_on_dev: bool = False
    debug_mode: bool = False
    timezone: str = "US/Eastern"
    
    # API server settings
    serve_port: int = 5001
    serve_host: str = "0.0.0.0"
    
    # Model settings
    lightgbm_params: Optional[dict] = None
    lstm_sequence_length: int = 4
    ensemble_weights: Optional[dict] = None
    
    # Data source settings - PRODUCTION MODE
    mock_mode: bool = False  # FIXED: Always use real data in production
    api_timeout: int = 30
    
    def __post_init__(self):
        """Initialize default values for complex fields"""
        if self.lightgbm_params is None:
            self.lightgbm_params = {
                'objective': 'regression',
                'metric': 'rmse',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': -1
            }
            
        if self.ensemble_weights is None:
            self.ensemble_weights = {
                'lightgbm': 0.7,
                'lstm': 0.3
            }

def load_config() -> Config:
    """Load configuration from environment variables"""
    
    config = Config()
    
    # Load from environment with defaults
    config.after_close_enabled = os.getenv('AFTER_CLOSE_ENABLED', 'true').lower() == 'true'
    config.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', '0.70'))  # Base only, see get_adaptive_confidence_threshold()
    config.symbol = os.getenv('SYMBOL', 'AMD')
    
    # Paths
    config.prediction_path = os.getenv('PREDICTION_PATH', config.prediction_path)
    config.log_path = os.getenv('LOG_PATH', config.log_path)
    config.snapshot_path = os.getenv('SNAPSHOT_PATH', config.snapshot_path)
    
    # Development
    config.auto_fit_on_dev = os.getenv('AUTO_FIT_ON_DEV', 'false').lower() == 'true'
    config.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    config.timezone = os.getenv('TIMEZONE', config.timezone)
    
    # API server
    config.serve_port = int(os.getenv('SERVE_PORT', str(config.serve_port)))
    config.serve_host = os.getenv('SERVE_HOST', config.serve_host)
    
    # Mock mode for development
    config.mock_mode = os.getenv('MOCK_MODE', 'false').lower() == 'true'
    
    return config

def get_adaptive_confidence_threshold() -> float:
    """Calculate adaptive confidence threshold based on current market conditions"""
    try:
        import yfinance as yf
        import numpy as np
        
        # Start with base threshold
        base_threshold = CONFIG.confidence_threshold
        
        # Adjust based on VIX (market volatility/fear)
        try:
            vix_data = yf.download("^VIX", period="2d", progress=False)
            if vix_data is not None and not vix_data.empty:
                current_vix = float(vix_data['Close'].iloc[-1])
                
                # When VIX is high (fear/uncertainty), require higher confidence
                # When VIX is low (complacency), can accept lower confidence
                if current_vix > 35:  # Extreme fear
                    base_threshold = 0.85  # Very high confidence required
                elif current_vix > 30:  # High fear
                    base_threshold = 0.80
                elif current_vix > 25:  # Elevated fear
                    base_threshold = 0.75
                elif current_vix < 12:  # Very low fear/complacency
                    base_threshold = 0.60  # Can accept lower confidence
                elif current_vix < 15:  # Low fear
                    base_threshold = 0.65
        except:
            pass
        
        # Adjust based on AMD's recent volatility
        try:
            amd_data = yf.download("AMD", period="10d", progress=False)
            if amd_data is not None and len(amd_data) >= 5:
                returns = amd_data['Close'].pct_change().dropna()
                if len(returns) >= 3:
                    volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                    
                    # Higher volatility = higher confidence required
                    if volatility > 0.50:  # Very high volatility
                        base_threshold += 0.10
                    elif volatility > 0.40:  # High volatility
                        base_threshold += 0.05
                    elif volatility < 0.20:  # Low volatility
                        base_threshold -= 0.05
        except:
            pass
        
        # Keep within reasonable bounds
        return max(0.55, min(0.90, base_threshold))
        
    except:
        # Safe fallback
        return CONFIG.confidence_threshold

# Global configuration instance
CONFIG = load_config()