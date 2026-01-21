"""
Feature engineering for After Close Engine
Creates normalized features from raw overnight data
"""
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import CONFIG

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Feature engineering pipeline for overnight predictions"""
    
    def __init__(self):
        self.scaler: Optional[StandardScaler] = None
        self.feature_names = [
            'overnight_futures_pct',
            'net_options_flow', 
            'news_sentiment_score',
            'global_index_impact_score',
            'prior_close_return',
            'intraday_volatility'
        ]
        self.scaler_path = os.path.join(CONFIG.model_path, 'feature_scaler.joblib')
        
    def create_features(self, raw_data: Dict) -> Dict[str, float]:
        """
        Create engineered features from raw overnight data
        Returns: Dictionary of normalized features
        """
        
        features = {}
        
        try:
            # 1. Overnight futures percentage
            futures_data = raw_data.get('futures', {})
            es_pct = futures_data.get('ES_pct', 0.0)
            nq_pct = futures_data.get('NQ_pct', 0.0)
            # Weighted average (NQ more relevant for tech stocks like AMD)
            features['overnight_futures_pct'] = 0.3 * es_pct + 0.7 * nq_pct
            
            # 2. Net options flow
            options_data = raw_data.get('options', {})
            call_flow = options_data.get('call_flow', 0)
            put_flow = options_data.get('put_flow', 0)
            total_flow = call_flow + put_flow
            
            if total_flow > 0:
                # Positive = more put flow (bearish), Negative = more call flow (bullish)
                features['net_options_flow'] = (put_flow - call_flow) / total_flow
            else:
                features['net_options_flow'] = 0.0
                
            # 3. News sentiment score  
            news_data = raw_data.get('news', {})
            features['news_sentiment_score'] = news_data.get('sentiment_score', 0.0)
            
            # 4. Global index impact score (weighted average)
            global_data = raw_data.get('global_indices', {})
            weights = {
                'nikkei_pct': 0.3,      # Asia impact
                'hang_seng_pct': 0.2,   # China impact
                'ftse_pct': 0.2,        # Europe impact
                'dax_pct': 0.2,         # Europe impact
                'cac40_pct': 0.1        # Europe impact
            }
            
            global_impact = 0.0
            for index, weight in weights.items():
                global_impact += weight * global_data.get(index, 0.0)
            features['global_index_impact_score'] = global_impact
            
            # 5. Prior close return (from snapshot)
            snapshot_data = raw_data.get('snapshot')
            if snapshot_data and 'prior_close_return' in snapshot_data:
                features['prior_close_return'] = snapshot_data['prior_close_return']
            else:
                features['prior_close_return'] = 0.0
                
            # 6. Intraday volatility (from snapshot)  
            if snapshot_data and 'intraday_volatility' in snapshot_data:
                features['intraday_volatility'] = snapshot_data['intraday_volatility']
            else:
                features['intraday_volatility'] = 0.0
                
            logger.info(f"Created {len(features)} features successfully")
            return features
            
        except Exception as e:
            logger.error(f"Feature creation failed: {e}")
            # Return safe defaults
            return {name: 0.0 for name in self.feature_names}
    
    def normalize_features(self, features: Dict[str, float]) -> np.ndarray[Any, Any]:
        """
        Normalize features using fitted scaler
        Returns: Numpy array of normalized features
        """
        
        try:
            # Ensure we have all required features
            feature_vector = []
            for name in self.feature_names:
                feature_vector.append(features.get(name, 0.0))
            
            feature_array = np.array(feature_vector).reshape(1, -1)
            
            # Load or create scaler
            if self.scaler is None:
                self._load_or_create_scaler()
            
            # Create DataFrame with feature names to avoid sklearn warnings
            feature_df = pd.DataFrame(feature_array, columns=self.feature_names)
            
            # Normalize features
            if self.scaler is not None:
                normalized = self.scaler.transform(feature_df)
                logger.debug(f"Features normalized successfully")
                return normalized[0]
            else:
                logger.warning("No scaler available, returning raw features")
                return feature_array[0]
                
        except Exception as e:
            logger.error(f"Feature normalization failed: {e}")
            return np.zeros(len(self.feature_names))
    
    def _load_or_create_scaler(self):
        """Load existing scaler or create new one from historical data"""
        
        # Try to load existing scaler
        if os.path.exists(self.scaler_path):
            try:
                self.scaler = joblib.load(self.scaler_path)
                logger.info(f"Loaded scaler from {self.scaler_path}")
                return
            except Exception as e:
                logger.warning(f"Failed to load scaler: {e}")
        
        # Create new scaler from historical data
        self._create_scaler_from_historical_data()
    
    def _create_scaler_from_historical_data(self):
        """Create and fit scaler from historical CSV data"""
        
        historical_path = os.path.join(CONFIG.sample_data_path, 'historical_features.csv')
        
        try:
            if os.path.exists(historical_path):
                # Load historical data
                df = pd.read_csv(historical_path)
                
                # Ensure we have required columns
                missing_cols = [col for col in self.feature_names if col not in df.columns]
                if missing_cols:
                    logger.warning(f"Missing columns in historical data: {missing_cols}")
                    # Add missing columns with zeros
                    for col in missing_cols:
                        df[col] = 0.0
                
                # Fit scaler
                self.scaler = StandardScaler()
                self.scaler.fit(df[self.feature_names])
                
                # Save scaler
                os.makedirs(CONFIG.model_path, exist_ok=True)
                joblib.dump(self.scaler, self.scaler_path)
                
                logger.info(f"Created and saved scaler from {len(df)} historical samples")
                
            else:
                logger.warning(f"Historical data not found: {historical_path}")
                logger.warning("Creating identity scaler (no normalization)")
                
                # Create identity scaler (no actual scaling)
                self.scaler = StandardScaler()
                # Fit with dummy data to avoid errors
                dummy_data = np.zeros((10, len(self.feature_names)))
                dummy_data += np.random.normal(0, 0.1, dummy_data.shape)
                self.scaler.fit(dummy_data)
                
                # Save dummy scaler
                os.makedirs(CONFIG.model_path, exist_ok=True) 
                joblib.dump(self.scaler, self.scaler_path)
                
        except Exception as e:
            logger.error(f"Failed to create scaler: {e}")
            self.scaler = None
    
    def create_sequence_features(self, feature_history: List[Dict]) -> Optional[np.ndarray]:
        """
        Create sequence features for LSTM model from feature history
        Returns: Numpy array suitable for LSTM input or None
        """
        
        try:
            if len(feature_history) < CONFIG.lstm_sequence_length:
                logger.debug(f"Insufficient history for LSTM: {len(feature_history)} < {CONFIG.lstm_sequence_length}")
                return None
            
            # Take last N sequences
            recent_history = feature_history[-CONFIG.lstm_sequence_length:]
            
            # Convert to normalized feature matrix
            sequence_matrix = []
            for features_dict in recent_history:
                normalized = self.normalize_features(features_dict)
                sequence_matrix.append(normalized)
            
            sequence_array = np.array(sequence_matrix)
            logger.debug(f"Created LSTM sequence: shape {sequence_array.shape}")
            
            return sequence_array
            
        except Exception as e:
            logger.error(f"Sequence feature creation failed: {e}")
            return None

def create_pipeline_features(raw_data: Dict, feature_history: Optional[List[Dict]] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Main pipeline function to create all features
    Returns: (tabular_features, sequence_features)
    """
    
    engineer = FeatureEngineer()
    
    # Create basic features
    features = engineer.create_features(raw_data)
    tabular_features = engineer.normalize_features(features)
    
    # Create sequence features if history available
    sequence_features = None
    if feature_history:
        sequence_features = engineer.create_sequence_features(feature_history)
    
    return tabular_features, sequence_features