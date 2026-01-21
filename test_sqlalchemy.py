#!/usr/bin/env python3
"""
Test SQLAlchemy database connection in Replit environment
"""
import os

def test_sqlalchemy_connection():
    """Test database connection using SQLAlchemy"""
    try:
        import sqlalchemy
        from sqlalchemy import create_engine, text
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            print("❌ No DATABASE_URL found")
            return False
            
        print(f"🔗 DATABASE_URL found: {DATABASE_URL[:50]}...")
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ SQLAlchemy works! PostgreSQL version: {version[:50]}...")
            
            # Test if our tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('predictions', 'prediction_outcomes')
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📊 Found tables: {tables}")
            
            # Test insert
            result = conn.execute(text("""
                INSERT INTO predictions (
                    symbol, prediction_type, prediction_date, direction, 
                    confidence, trade_signal, model_version, data_quality, 
                    data_sources_count, feature_count, is_active, dry_run,
                    prediction_data
                ) VALUES (
                    'TEST', 'test', CURRENT_DATE, 'UP', 
                    0.75, 'BUY', 'test_v1', 'GOOD',
                    1, 1, true, true,
                    '{"test": true}'::jsonb
                ) RETURNING id
            """))
            
            prediction_id = result.fetchone()[0]
            print(f"✅ Test prediction saved with ID: {prediction_id}")
            
            # Clean up test data
            conn.execute(text("DELETE FROM predictions WHERE symbol = 'TEST'"))
            conn.commit()
            print("✅ Test data cleaned up")
            
        return True
        
    except ImportError as e:
        print(f"❌ SQLAlchemy not available: {e}")
        return False
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing SQLAlchemy database connection...")
    if test_sqlalchemy_connection():
        print("✅ SQLAlchemy database connection works!")
    else:
        print("❌ SQLAlchemy database connection failed")