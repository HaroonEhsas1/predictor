#!/usr/bin/env python3
"""
Command-line interface for Next-Day Prediction Engine
Professional institutional-grade prediction system
"""

import argparse
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from .predict import run_prediction_cli
    from .config import CONFIG, update_config
except ImportError:
    from predict import run_prediction_cli
    from config import CONFIG, update_config

def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Next-Day Prediction Engine - Institutional Grade Gap Predictions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                           # Generate prediction (dry run)
  python cli.py --train                   # Train new models
  python cli.py --enable                  # Enable feature flag
  python cli.py --confidence 0.85         # Set confidence threshold
  python cli.py --model-version 20250819  # Use specific model version
  python cli.py --status                  # Show system status
        """
    )
    
    # Main actions
    parser.add_argument('--train', action='store_true',
                       help='Train new models using historical data')
    parser.add_argument('--predict', action='store_true', default=True,
                       help='Generate next-day prediction (default)')
    parser.add_argument('--status', action='store_true',
                       help='Show system status and configuration')
    
    # Configuration
    parser.add_argument('--enable', action='store_true',
                       help='Enable next-day prediction feature')
    parser.add_argument('--disable', action='store_true',
                       help='Disable next-day prediction feature')
    parser.add_argument('--dry-run', type=bool, default=None,
                       help='Enable/disable dry run mode (default: True)')
    parser.add_argument('--confidence', type=float,
                       help='Set minimum confidence threshold (default: 0.80)')
    parser.add_argument('--consensus', type=float,
                       help='Set minimum ensemble consensus threshold (default: 0.80)')
    
    # Model options  
    parser.add_argument('--model-version', type=str,
                       help='Specific model version to use (default: latest)')
    parser.add_argument('--lookback-days', type=int, default=60,
                       help='Days of historical data for features (default: 60)')
    
    # Testing
    parser.add_argument('--test', action='store_true',
                       help='Run unit tests')
    
    args = parser.parse_args()
    
    print("🔮 NEXT-DAY PREDICTION ENGINE")
    print("⚖️ Institutional-Grade Gap Predictions")
    print("=" * 50)
    
    # Handle configuration updates
    config_updates = {}
    
    if args.enable:
        config_updates['enabled'] = True
        print("✓ Feature enabled")
    
    if args.disable:
        config_updates['enabled'] = False
        print("✓ Feature disabled")
    
    if args.dry_run is not None:
        config_updates['dry_run'] = args.dry_run
        print(f"✓ Dry run: {args.dry_run}")
    
    if args.confidence:
        if not 0.5 <= args.confidence <= 1.0:
            print("✗ Error: Confidence must be between 0.5 and 1.0")
            sys.exit(1)
        config_updates['min_confidence'] = args.confidence
        print(f"✓ Confidence threshold: {args.confidence:.0%}")
    
    if args.consensus:
        if not 0.5 <= args.consensus <= 1.0:
            print("✗ Error: Consensus must be between 0.5 and 1.0")
            sys.exit(1)
        config_updates['min_ensemble_consensus'] = args.consensus
        print(f"✓ Consensus threshold: {args.consensus:.0%}")
    
    if config_updates:
        update_config(config_updates)
        print()
    
    # Handle main actions
    if args.test:
        print("🧪 Running unit tests...")
        try:
            from tests.test_nextday import run_tests
            success = run_tests()
            sys.exit(0 if success else 1)
        except ImportError as e:
            print(f"✗ Failed to import tests: {e}")
            sys.exit(1)
    
    elif args.status:
        show_status()
    
    elif args.train or not args.predict:
        # Training mode
        try:
            run_prediction_cli(
                model_version=args.model_version,
                train_mode=True,
                lookback_days=args.lookback_days
            )
        except Exception as e:
            print(f"✗ Training failed: {e}")
            sys.exit(1)
    
    else:
        # Prediction mode (default)
        try:
            run_prediction_cli(
                model_version=args.model_version,
                train_mode=False,
                lookback_days=args.lookback_days
            )
        except Exception as e:
            print(f"✗ Prediction failed: {e}")
            sys.exit(1)

def show_status():
    """Show current system status"""
    
    print("📊 SYSTEM STATUS")
    print("-" * 30)
    
    print(f"Feature Enabled: {CONFIG.enabled}")
    print(f"Dry Run Mode: {CONFIG.dry_run}")
    print(f"Confidence Threshold: {CONFIG.min_confidence:.0%}")
    print(f"Consensus Threshold: {CONFIG.min_ensemble_consensus:.0%}")
    print(f"Max Position Size: {CONFIG.max_position_size:.1%}")
    print(f"Models Path: {CONFIG.models_path}")
    print(f"Data Path: {CONFIG.data_path}")
    
    # Check for trained models
    import glob
    model_files = glob.glob(os.path.join(CONFIG.models_path, "*.pkl"))
    print(f"Trained Models: {len(model_files)} files found")
    
    if model_files:
        latest_model = max(model_files, key=os.path.getmtime)
        model_date = datetime.fromtimestamp(os.path.getmtime(latest_model))
        print(f"Latest Model: {os.path.basename(latest_model)} ({model_date.strftime('%Y-%m-%d %H:%M')})")
    
    # Try to initialize predictor for health check
    try:
        from predict import NextDayPredictor
        predictor = NextDayPredictor()
        status = predictor.get_status()
        
        print(f"Predictor Health: {'✓ Ready' if status['models_loaded'] else '✗ Not Ready'}")
        print(f"Scaler Fitted: {'✓ Yes' if status['scaler_fitted'] else '✗ No'}")
        
    except Exception as e:
        print(f"Predictor Health: ✗ Error - {e}")

if __name__ == '__main__':
    main()