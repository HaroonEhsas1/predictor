"""
Optional Flask API server for After Close Engine
Provides HTTP endpoints for prediction access and health checks
"""
import logging
import json
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import CONFIG

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    CORS(app)
    
    # Configure logging
    if CONFIG.debug_mode:
        app.logger.setLevel(logging.DEBUG)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'engine': 'after_close_engine',
            'version': '1.0'
        })
    
    @app.route('/status', methods=['GET'])
    def status():
        """Engine status and last run information"""
        
        try:
            # Check if prediction file exists
            prediction_path = os.path.join(CONFIG.prediction_path, 'latest.json')
            
            if os.path.exists(prediction_path):
                with open(prediction_path, 'r') as f:
                    latest_prediction = json.load(f)
                
                file_stats = os.stat(prediction_path)
                last_modified = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                
                return jsonify({
                    'status': 'active',
                    'last_prediction_time': latest_prediction.get('timestamp'),
                    'last_file_modified': last_modified,
                    'prediction_available': True,
                    'confidence': latest_prediction.get('confidence'),
                    'direction': latest_prediction.get('direction')
                })
            else:
                return jsonify({
                    'status': 'no_predictions',
                    'prediction_available': False,
                    'message': 'No predictions generated yet'
                })
                
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.route('/after_close/prediction', methods=['GET'])
    def get_prediction():
        """Get latest after-close prediction"""
        
        try:
            prediction_path = os.path.join(CONFIG.prediction_path, 'latest.json')
            
            if not os.path.exists(prediction_path):
                return jsonify({
                    'error': 'No prediction available',
                    'message': 'Run engine.py predict to generate predictions'
                }), 404
            
            # Read latest prediction
            with open(prediction_path, 'r') as f:
                prediction = json.load(f)
            
            # Add metadata
            file_stats = os.stat(prediction_path)
            prediction['file_modified'] = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            
            return jsonify(prediction)
            
        except Exception as e:
            logger.error(f"Failed to get prediction: {e}")
            return jsonify({
                'error': 'Failed to read prediction',
                'message': str(e)
            }), 500
    
    @app.route('/after_close/history', methods=['GET'])
    def get_prediction_history():
        """Get prediction history (optional feature)"""
        
        try:
            # Get optional limit parameter
            limit = request.args.get('limit', default=10, type=int)
            limit = min(limit, 100)  # Cap at 100
            
            # Look for historical log files
            log_dir = CONFIG.log_path
            history = []
            
            if os.path.exists(log_dir):
                log_files = [f for f in os.listdir(log_dir) if f.startswith('prediction-') and f.endswith('.log')]
                log_files.sort(reverse=True)  # Most recent first
                
                for log_file in log_files[:limit]:
                    file_path = os.path.join(log_dir, log_file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            # Try to extract JSON from log
                            if 'PREDICTION:' in content:
                                json_start = content.find('{')
                                json_end = content.rfind('}') + 1
                                if json_start != -1 and json_end > json_start:
                                    pred_data = json.loads(content[json_start:json_end])
                                    history.append(pred_data)
                    except Exception as e:
                        logger.warning(f"Failed to parse log file {log_file}: {e}")
            
            return jsonify({
                'history': history,
                'count': len(history),
                'limit': limit
            })
            
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return jsonify({
                'error': 'Failed to get prediction history',
                'message': str(e)
            }), 500
    
    return app

def start_server():
    """Start Flask development server"""
    
    if not CONFIG.after_close_enabled:
        logger.error("After Close Engine is disabled. Set AFTER_CLOSE_ENABLED=true to enable.")
        return
    
    logger.info(f"Starting After Close Engine API server on {CONFIG.serve_host}:{CONFIG.serve_port}")
    
    app = create_app()
    
    try:
        app.run(
            host=CONFIG.serve_host,
            port=CONFIG.serve_port,
            debug=CONFIG.debug_mode,
            use_reloader=False  # Prevent double startup in debug mode
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")

if __name__ == '__main__':
    start_server()