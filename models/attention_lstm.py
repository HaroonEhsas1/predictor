#!/usr/bin/env python3
"""
Attention-Enhanced LSTM/GRU Models - 2025 State-of-the-Art
Research shows significant improvement over vanilla LSTM/GRU
100% FREE - Uses TensorFlow/Keras
"""

import numpy as np
from typing import Tuple, Optional, Dict, Any

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, Model
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Install with: pip install tensorflow")


class AttentionLayer(layers.Layer):
    """
    Attention Mechanism for LSTM/GRU
    
    Allows the model to focus on important time steps automatically
    Based on Bahdanau attention mechanism (2015) - widely used in 2025
    """
    
    def __init__(self, units: int = 64, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        self.units = units
        
    def build(self, input_shape):
        self.W = self.add_weight(
            name='attention_weight',
            shape=(input_shape[-1], self.units),
            initializer='glorot_uniform',
            trainable=True
        )
        self.b = self.add_weight(
            name='attention_bias',
            shape=(self.units,),
            initializer='zeros',
            trainable=True
        )
        self.u = self.add_weight(
            name='attention_vector',
            shape=(self.units,),
            initializer='glorot_uniform',
            trainable=True
        )
        super(AttentionLayer, self).build(input_shape)
    
    def call(self, inputs):
        # inputs shape: (batch_size, time_steps, features)
        
        # Calculate attention scores
        score = tf.nn.tanh(tf.tensordot(inputs, self.W, axes=1) + self.b)
        attention_weights = tf.nn.softmax(tf.tensordot(score, self.u, axes=1), axis=1)
        
        # Apply attention weights
        attention_weights = tf.expand_dims(attention_weights, -1)
        weighted_input = inputs * attention_weights
        
        return tf.reduce_sum(weighted_input, axis=1)
    
    def get_config(self):
        config = super().get_config()
        config.update({'units': self.units})
        return config


class AttentionLSTM:
    """
    LSTM with Attention Mechanism - 2025 Architecture
    
    Features:
    - Bidirectional LSTM for past and future context
    - Attention mechanism to focus on important patterns
    - Dropout for regularization
    - Early stopping to prevent overfitting
    """
    
    def __init__(self, sequence_length: int, n_features: int, 
                 lstm_units: int = 128, attention_units: int = 64,
                 dropout_rate: float = 0.2):
        """
        Args:
            sequence_length: Number of time steps in input
            n_features: Number of features per time step
            lstm_units: LSTM hidden units
            attention_units: Attention mechanism units
            dropout_rate: Dropout rate for regularization
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow required for Attention LSTM")
        
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.lstm_units = lstm_units
        self.attention_units = attention_units
        self.dropout_rate = dropout_rate
        self.model = None
        self.history = None
        
        self._build_model()
    
    def _build_model(self):
        """Build Attention-LSTM architecture"""
        
        # Input layer
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))
        
        # Bidirectional LSTM (captures past and future context)
        lstm_out = layers.Bidirectional(
            layers.LSTM(self.lstm_units, return_sequences=True, dropout=self.dropout_rate)
        )(inputs)
        
        # Attention mechanism
        attention_out = AttentionLayer(units=self.attention_units)(lstm_out)
        
        # Dense layers for prediction
        dense1 = layers.Dense(64, activation='relu')(attention_out)
        dense1 = layers.Dropout(self.dropout_rate)(dense1)
        
        dense2 = layers.Dense(32, activation='relu')(dense1)
        dense2 = layers.Dropout(self.dropout_rate)(dense2)
        
        # Output layer (regression)
        outputs = layers.Dense(1, activation='linear')(dense2)
        
        # Create model
        self.model = Model(inputs=inputs, outputs=outputs)
        
        # Compile with Adam optimizer
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
    
    def fit(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2,
            epochs: int = 100, batch_size: int = 32) -> Dict[str, Any]:
        """
        Train the Attention-LSTM model
        
        Args:
            X: Training features (n_samples, sequence_length, n_features)
            y: Training targets (n_samples,)
            validation_split: Fraction for validation
            epochs: Maximum training epochs
            batch_size: Batch size for training
        """
        print(f"🚀 Training Attention-LSTM...")
        print(f"   Architecture: BiLSTM({self.lstm_units}) + Attention({self.attention_units})")
        
        # Callbacks for better training
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        # Train
        self.history = self.model.fit(
            X, y,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=0
        )
        
        # Extract metrics
        train_loss = self.history.history['loss'][-1]
        val_loss = self.history.history['val_loss'][-1]
        train_mae = self.history.history['mae'][-1]
        val_mae = self.history.history['val_mae'][-1]
        
        print(f"\n✅ Training Complete!")
        print(f"   📊 Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        print(f"   📈 Train MAE: {train_mae:.4f} | Val MAE: {val_mae:.4f}")
        
        return {
            'train_loss': train_loss,
            'val_loss': val_loss,
            'train_mae': train_mae,
            'val_mae': val_mae,
            'epochs_trained': len(self.history.history['loss'])
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        return self.model.predict(X, verbose=0).flatten()
    
    def save(self, filepath: str):
        """Save model to file"""
        self.model.save(filepath)
    
    def load(self, filepath: str):
        """Load model from file"""
        self.model = keras.models.load_model(
            filepath,
            custom_objects={'AttentionLayer': AttentionLayer}
        )


class AttentionGRU:
    """
    GRU with Attention Mechanism - Faster alternative to LSTM
    
    GRU is computationally more efficient than LSTM while maintaining similar performance
    """
    
    def __init__(self, sequence_length: int, n_features: int,
                 gru_units: int = 128, attention_units: int = 64,
                 dropout_rate: float = 0.2):
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow required for Attention GRU")
        
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.gru_units = gru_units
        self.attention_units = attention_units
        self.dropout_rate = dropout_rate
        self.model = None
        self.history = None
        
        self._build_model()
    
    def _build_model(self):
        """Build Attention-GRU architecture"""
        
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))
        
        # Bidirectional GRU
        gru_out = layers.Bidirectional(
            layers.GRU(self.gru_units, return_sequences=True, dropout=self.dropout_rate)
        )(inputs)
        
        # Attention mechanism
        attention_out = AttentionLayer(units=self.attention_units)(gru_out)
        
        # Dense layers
        dense1 = layers.Dense(64, activation='relu')(attention_out)
        dense1 = layers.Dropout(self.dropout_rate)(dense1)
        
        dense2 = layers.Dense(32, activation='relu')(dense1)
        outputs = layers.Dense(1, activation='linear')(dense2)
        
        self.model = Model(inputs=inputs, outputs=outputs)
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
    
    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """Train GRU with attention (same interface as AttentionLSTM)"""
        return AttentionLSTM.fit(self, X, y, **kwargs)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        return self.model.predict(X, verbose=0).flatten()


if __name__ == "__main__":
    if TENSORFLOW_AVAILABLE:
        print("Testing Attention-Enhanced LSTM (2025 Architecture)...")
        
        # Generate sample time series data
        sequence_length = 60
        n_features = 10
        n_samples = 1000
        
        X = np.random.randn(n_samples, sequence_length, n_features)
        y = np.random.randn(n_samples)
        
        # Train Attention-LSTM
        model = AttentionLSTM(
            sequence_length=sequence_length,
            n_features=n_features,
            lstm_units=64,
            attention_units=32
        )
        
        metrics = model.fit(X, y, epochs=10, batch_size=32)
        
        # Make predictions
        predictions = model.predict(X[:10])
        print(f"\n📊 Sample Predictions: {predictions}")
        
        print("\n✅ Attention-LSTM: State-of-the-art for time series (2025)")
    else:
        print("⚠️ TensorFlow not available. Install with: pip install tensorflow")
