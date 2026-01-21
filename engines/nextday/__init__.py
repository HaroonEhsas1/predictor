"""
Professional Next-Day Prediction Engine
Institutional-grade gap prediction with comprehensive validation
"""

from .predict import NextDayPredictor, run_prediction_cli
from .config import CONFIG, update_config
from .gate import PredictionGate, RiskManager

__version__ = "1.0.0"
__all__ = ['NextDayPredictor', 'run_prediction_cli', 'CONFIG', 'update_config', 'PredictionGate', 'RiskManager']