#!/usr/bin/env python3
"""
After Close Engine - Main CLI interface
Independent overnight gap prediction engine for AMD stock
"""
import argparse
import json
import logging
import os
import tempfile
from datetime import datetime
from typing import Dict, Optional

# Engine modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import CONFIG
from fetchers import collect_all_data
from features import create_pipeline_features
from model_training import EnsembleModel, auto_fit_models
# Optional import for serve functionality
try:
    from serve import start_server
    SERVE_AVAILABLE = True
except ImportError:
    SERVE_AVAILABLE = False

def setup_logging(debug: bool = False):
    """Configure logging for the engine"""
    
    level = logging.DEBUG if debug else logging.INFO
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # File handler
    os.makedirs(CONFIG.log_path, exist_ok=True)
    log_file = os.path.join(CONFIG.log_path, f'engine-{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def collect_command() -> Dict:
    """Execute data collection command"""
    
    logger = logging.getLogger(__name__)
    logger.info("Starting data collection...")
    
    try:
        data = collect_all_data(CONFIG.symbol)
        
        # Save collected data for inspection
        os.makedirs(CONFIG.prediction_path, exist_ok=True)
        collection_file = os.path.join(CONFIG.prediction_path, 'latest_collection.json')
        
        with open(collection_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Data collection completed, saved to {collection_file}")
        return {
            'status': 'success',
            'data': data,
            'collection_file': collection_file
        }
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def predict_command(dry_run: bool = False, auto_fit: bool = False) -> Dict:
    """Execute prediction command"""
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting prediction (dry_run={dry_run}, auto_fit={auto_fit})...")
    
    try:
        # Check if engine is enabled
        if not CONFIG.after_close_enabled and not dry_run:
            logger.error("After Close Engine is disabled. Set AFTER_CLOSE_ENABLED=true to enable.")
            return {
                'status': 'disabled',
                'message': 'Engine disabled in configuration'
            }
        
        # Auto-fit models if requested or in dev mode
        if auto_fit or (CONFIG.auto_fit_on_dev and CONFIG.debug_mode):
            logger.info("Auto-fitting models...")
            fit_results = auto_fit_models(force_retrain=auto_fit)
            if fit_results.get('status') == 'error':
                logger.error(f"Auto-fit failed: {fit_results.get('message')}")
                return {
                    'status': 'error',
                    'error': 'Model auto-fit failed',
                    'details': fit_results
                }
        
        # Load ensemble model
        ensemble = EnsembleModel()
        if not ensemble.load():
            logger.error("Failed to load models. Run with --auto-fit to train models first.")
            return {
                'status': 'error',
                'error': 'No trained models available'
            }
        
        # Collect fresh data
        logger.info("Collecting overnight data...")
        raw_data = collect_all_data(CONFIG.symbol)
        
        if 'error' in raw_data:
            logger.error(f"Data collection failed: {raw_data['error']}")
            return {
                'status': 'error',
                'error': 'Data collection failed',
                'details': raw_data
            }
        
        # Create features
        logger.info("Engineering features...")
        tabular_features, sequence_features = create_pipeline_features(raw_data)
        
        # Make prediction
        logger.info("Generating prediction...")
        prediction_value, model_predictions = ensemble.predict(tabular_features, sequence_features)
        
        # Convert to direction and expected price
        current_price = raw_data.get('futures', {}).get('current_amd_price', 168.0)  # Default fallback
        expected_open = current_price + prediction_value
        
        # Determine direction
        if prediction_value > 0.5:
            direction = "UP"
        elif prediction_value < -0.5:
            direction = "DOWN"
        else:
            direction = "SKIP"  # Low confidence/neutral
        
        # Calculate confidence based on prediction magnitude
        confidence = min(abs(prediction_value) / 2.0, 1.0)  # Scale to 0-1
        
        # Apply confidence gating
        if confidence < CONFIG.confidence_threshold:
            direction = "SKIP"
            logger.info(f"Low confidence {confidence:.3f} < {CONFIG.confidence_threshold}, setting direction to SKIP")
        
        # Create prediction dictionary
        prediction = {
            'timestamp': datetime.now().isoformat(),
            'symbol': CONFIG.symbol,
            'direction': direction,
            'expected_open': round(expected_open, 2),
            'confidence': round(confidence, 3),
            'prediction_value': round(prediction_value, 4),
            'current_price': current_price,
            'features': {
                'overnight_futures_pct': round(tabular_features[0], 4),
                'net_options_flow': round(tabular_features[1], 4),
                'news_sentiment_score': round(tabular_features[2], 4),
                'global_index_impact_score': round(tabular_features[3], 4),
                'prior_close_return': round(tabular_features[4], 4),
                'intraday_volatility': round(tabular_features[5], 4)
            },
            'model_predictions': {
                'lightgbm': round(model_predictions['lightgbm'], 4),
                'lstm': round(model_predictions['lstm'], 4)
            },
            'model_version': 'v1.0',
            'confidence_threshold': CONFIG.confidence_threshold
        }
        
        logger.info(f"Prediction generated: {direction} with {confidence:.1%} confidence")
        
        if dry_run:
            logger.info("DRY RUN - Prediction not saved to file")
            print(f"\nPREDICTION (DRY RUN):")
            print(json.dumps(prediction, indent=2))
            return {
                'status': 'success_dry_run',
                'prediction': prediction
            }
        
        # Write prediction to file (atomic write)
        os.makedirs(CONFIG.prediction_path, exist_ok=True)
        prediction_file = os.path.join(CONFIG.prediction_path, 'latest.json')
        
        with tempfile.NamedTemporaryFile(mode='w', dir=CONFIG.prediction_path, delete=False) as temp_file:
            json.dump(prediction, temp_file, indent=2)
            temp_file_path = temp_file.name
        
        os.rename(temp_file_path, prediction_file)
        logger.info(f"Prediction saved to {prediction_file}")
        
        # Write human-readable log
        log_file = os.path.join(CONFIG.log_path, f'prediction-{datetime.now().strftime("%Y%m%d-%H%M%S")}.log')
        with open(log_file, 'w') as f:
            f.write(f"After Close Engine Prediction\n")
            f.write(f"Generated: {prediction['timestamp']}\n")
            f.write(f"Symbol: {prediction['symbol']}\n")
            f.write(f"Direction: {prediction['direction']}\n")
            f.write(f"Expected Open: ${prediction['expected_open']}\n")
            f.write(f"Confidence: {prediction['confidence']:.1%}\n")
            f.write(f"\nFull Prediction JSON:\n")
            f.write(json.dumps(prediction, indent=2))
        
        return {
            'status': 'success',
            'prediction': prediction,
            'prediction_file': prediction_file,
            'log_file': log_file
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(description='After Close Engine - Overnight Gap Prediction')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect overnight data')
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Generate prediction')
    predict_parser.add_argument('--mode', choices=['dry-run'], help='Prediction mode')
    predict_parser.add_argument('--auto-fit', action='store_true', help='Auto-fit models if missing')
    
    # Serve command  
    serve_parser = subparsers.add_parser('serve', help='Start API server')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    # Execute command
    if args.command == 'collect':
        result = collect_command()
        
    elif args.command == 'predict':
        dry_run = args.mode == 'dry-run'
        result = predict_command(dry_run=dry_run, auto_fit=args.auto_fit)
        
    elif args.command == 'serve':
        if SERVE_AVAILABLE:
            start_server()
        else:
            logger.error("Flask not available. Install flask and flask-cors to use serve mode.")
            exit(1)
        return
        
    else:
        parser.print_help()
        return
    
    # Print result
    if result.get('status') == 'success':
        logger.info("Command completed successfully")
    elif result.get('status') == 'success_dry_run':
        logger.info("Dry run completed successfully")
    else:
        logger.error(f"Command failed: {result.get('error', 'Unknown error')}")
        exit(1)

if __name__ == '__main__':
    main()