-- Prediction Storage Schema
-- This schema stores all prediction data to prevent memory-only storage issues

-- Main predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    prediction_type VARCHAR(20) NOT NULL, -- 'next_day', 'intraday', '1min', 'scalper', 'elite'
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    prediction_date DATE NOT NULL, -- The trading date this prediction is for
    
    -- Core prediction fields
    direction VARCHAR(10) NOT NULL, -- 'UP', 'DOWN', 'STABLE', 'HOLD'
    confidence DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    trade_signal VARCHAR(10) NOT NULL, -- 'BUY', 'SELL', 'HOLD', 'NO_TRADE'
    
    -- Price fields
    current_price DECIMAL(10,4),
    predicted_price DECIMAL(10,4),
    target_price_up DECIMAL(10,4),
    target_price_down DECIMAL(10,4),
    stop_loss DECIMAL(10,4),
    take_profit DECIMAL(10,4),
    
    -- Risk and position
    risk_level VARCHAR(10), -- 'LOW', 'MEDIUM', 'HIGH'
    position_size DECIMAL(10,4),
    expected_move_pct DECIMAL(8,4),
    risk_reward_ratio DECIMAL(8,4),
    
    -- Model and data quality
    model_version VARCHAR(50),
    data_quality VARCHAR(20), -- 'EXCELLENT', 'GOOD', 'FAIR', 'POOR'
    data_sources_count INTEGER DEFAULT 0,
    feature_count INTEGER DEFAULT 0,
    
    -- Status tracking
    is_active BOOLEAN DEFAULT TRUE,
    dry_run BOOLEAN DEFAULT FALSE,
    
    -- Detailed prediction data as JSON
    prediction_data JSONB, -- Full prediction details, components, signals, etc.
    
    -- Tracking fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Prediction outcomes table (for tracking accuracy)
CREATE TABLE IF NOT EXISTS prediction_outcomes (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER NOT NULL REFERENCES predictions(id),
    
    -- Actual results
    actual_price DECIMAL(10,4),
    actual_direction VARCHAR(10),
    price_difference DECIMAL(10,4),
    percentage_error DECIMAL(8,4),
    
    -- Accuracy metrics
    direction_correct BOOLEAN,
    confidence_appropriate BOOLEAN,
    within_target_range BOOLEAN,
    
    -- Outcome timestamp
    outcome_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_predictions_symbol_timestamp ON predictions(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_prediction_date ON predictions(prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_type_timestamp ON predictions(prediction_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_active ON predictions(is_active, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON predictions(confidence DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_predictions_symbol_type_date ON predictions(symbol, prediction_type, prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_recent_active ON predictions(timestamp DESC, is_active) WHERE is_active = TRUE;

-- Index on JSONB data for efficient queries on prediction components
CREATE INDEX IF NOT EXISTS idx_predictions_data_gin ON predictions USING GIN (prediction_data);

-- Outcome indexes
CREATE INDEX IF NOT EXISTS idx_outcomes_prediction_id ON prediction_outcomes(prediction_id);
CREATE INDEX IF NOT EXISTS idx_outcomes_accuracy ON prediction_outcomes(direction_correct, within_target_range);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_predictions_updated_at
    BEFORE UPDATE ON predictions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- View for recent predictions with key metrics
CREATE OR REPLACE VIEW recent_predictions AS
SELECT 
    id,
    symbol,
    prediction_type,
    timestamp,
    prediction_date,
    direction,
    confidence,
    trade_signal,
    current_price,
    predicted_price,
    risk_level,
    model_version,
    data_quality,
    is_active,
    dry_run,
    created_at
FROM predictions
WHERE timestamp >= NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;

-- View for prediction accuracy summary
CREATE OR REPLACE VIEW prediction_accuracy_summary AS
SELECT 
    p.prediction_type,
    p.symbol,
    COUNT(*) as total_predictions,
    COUNT(po.id) as evaluated_predictions,
    COUNT(CASE WHEN po.direction_correct = true THEN 1 END) as correct_direction,
    COUNT(CASE WHEN po.within_target_range = true THEN 1 END) as within_range,
    ROUND(
        COUNT(CASE WHEN po.direction_correct = true THEN 1 END)::decimal / 
        NULLIF(COUNT(po.id), 0) * 100, 2
    ) as direction_accuracy_pct,
    ROUND(
        COUNT(CASE WHEN po.within_target_range = true THEN 1 END)::decimal / 
        NULLIF(COUNT(po.id), 0) * 100, 2
    ) as target_accuracy_pct,
    AVG(p.confidence) as avg_confidence,
    AVG(ABS(po.percentage_error)) as avg_error_pct
FROM predictions p
LEFT JOIN prediction_outcomes po ON p.id = po.prediction_id
WHERE p.created_at >= NOW() - INTERVAL '30 days'
GROUP BY p.prediction_type, p.symbol
ORDER BY direction_accuracy_pct DESC;