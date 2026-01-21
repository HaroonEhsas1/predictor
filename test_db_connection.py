#!/usr/bin/env python3
"""
Test database connection and create schema if needed
"""
import os
import sys

def test_database_connection():
    """Test database connection with different drivers"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ No DATABASE_URL found")
        return False
    
    print(f"🔗 DATABASE_URL found: {DATABASE_URL[:50]}...")
    
    # Try different PostgreSQL drivers
    drivers_to_try = [
        ('psycopg2', 'psycopg2'),
        ('pg8000', 'pg8000'),
        ('psycopg2-binary', 'psycopg2'),
        ('asyncpg', 'asyncpg')
    ]
    
    for driver_name, import_name in drivers_to_try:
        try:
            print(f"🔍 Trying {driver_name}...")
            
            if import_name == 'psycopg2':
                import psycopg2
                from psycopg2.extras import RealDictCursor
                
                conn = psycopg2.connect(DATABASE_URL)
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT version();")
                    result = cur.fetchone()
                    print(f"✅ {driver_name} works! PostgreSQL version: {result['version'][:50]}...")
                conn.close()
                return True
                
            elif import_name == 'pg8000':
                import pg8000
                import sqlalchemy
                
                engine = sqlalchemy.create_engine(DATABASE_URL)
                conn = engine.connect()
                result = conn.execute(sqlalchemy.text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"✅ {driver_name} works! PostgreSQL version: {version[:50]}...")
                conn.close()
                return True
                
        except ImportError as e:
            print(f"⚠️ {driver_name} not available: {e}")
            continue
        except Exception as e:
            print(f"❌ {driver_name} connection failed: {e}")
            continue
    
    print("❌ No working PostgreSQL driver found")
    return False

def create_prediction_schema():
    """Create prediction tables if they don't exist"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        
        with conn.cursor() as cur:
            # Create predictions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    prediction_type VARCHAR(20) NOT NULL,
                    prediction_date DATE NOT NULL,
                    direction VARCHAR(10) NOT NULL,
                    confidence DECIMAL(5,4) NOT NULL,
                    trade_signal VARCHAR(20),
                    current_price DECIMAL(10,2),
                    predicted_price DECIMAL(10,2),
                    target_price_up DECIMAL(10,2),
                    target_price_down DECIMAL(10,2),
                    stop_loss DECIMAL(10,2),
                    take_profit DECIMAL(10,2),
                    risk_level VARCHAR(20),
                    position_size DECIMAL(10,2),
                    expected_move_pct DECIMAL(8,4),
                    risk_reward_ratio DECIMAL(8,4),
                    model_version VARCHAR(50),
                    data_quality VARCHAR(20),
                    data_sources_count INTEGER,
                    feature_count INTEGER,
                    is_active BOOLEAN DEFAULT true,
                    dry_run BOOLEAN DEFAULT false,
                    prediction_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create prediction_outcomes table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prediction_outcomes (
                    id SERIAL PRIMARY KEY,
                    prediction_id INTEGER REFERENCES predictions(id) ON DELETE CASCADE,
                    actual_price DECIMAL(10,2) NOT NULL,
                    actual_direction VARCHAR(10) NOT NULL,
                    price_difference DECIMAL(10,2),
                    percentage_error DECIMAL(8,4),
                    direction_correct BOOLEAN NOT NULL,
                    within_target_range BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indices
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_symbol_type_date 
                ON predictions(symbol, prediction_type, prediction_date);
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_created_at 
                ON predictions(created_at);
            """)
            
            conn.commit()
            print("✅ Database schema created/verified successfully")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create schema: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing database connection...")
    
    if test_database_connection():
        print("🔧 Creating/verifying schema...")
        if create_prediction_schema():
            print("✅ Database setup complete!")
        else:
            print("❌ Schema setup failed")
    else:
        print("❌ Database connection test failed")