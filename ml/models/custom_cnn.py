"""
Custom Baseline Convolutional Neural Network (CNN) for AgriVision Agent.
Demonstrates classical CNN feature extraction combined with an ANN dense classification head.
"""

from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers


def build_custom_cnn(
    num_classes: int = 3,
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    learning_rate: float = 0.0005,
    l2_reg: float = 0.0001
) -> tf.keras.Model:
    """
    Constructs a classical multi-layer CNN architecture:
    
    [Input Image 224x224x3]
         ↓
    [Conv2D (32 filters, 3x3, ReLU) + BatchNorm]
    [MaxPooling2D (2x2)]
         ↓
    [Conv2D (64 filters, 3x3, ReLU) + BatchNorm]
    [MaxPooling2D (2x2)]
         ↓
    [Conv2D (128 filters, 3x3, ReLU) + BatchNorm]
    [MaxPooling2D (2x2)]
         ↓
    [GlobalAveragePooling2D]
         ↓
    [ANN Dense Layer: 128 units, ReLU, L2 Reg]
    [Dropout (0.30)]
         ↓
    [ANN Dense Layer: 64 units, ReLU]
    [Dropout (0.20)]
         ↓
    [Softmax Output Layer: num_classes]
    """
    inputs = layers.Input(shape=input_shape, name="input_image")
    
    # Block 1
    x = layers.Conv2D(32, (3, 3), padding="same", activation="relu", name="conv1")(inputs)
    x = layers.BatchNormalization(name="bn1")(x)
    x = layers.MaxPooling2D((2, 2), name="pool1")(x)
    
    # Block 2
    x = layers.Conv2D(64, (3, 3), padding="same", activation="relu", name="conv2")(x)
    x = layers.BatchNormalization(name="bn2")(x)
    x = layers.MaxPooling2D((2, 2), name="pool2")(x)
    
    # Block 3
    x = layers.Conv2D(128, (3, 3), padding="same", activation="relu", name="conv3")(x)
    x = layers.BatchNormalization(name="bn3")(x)
    x = layers.MaxPooling2D((2, 2), name="pool3")(x)
    
    # Feature Aggregation (GAP2D)
    x = layers.GlobalAveragePooling2D(name="global_pool")(x)
    
    # Artificial Neural Network (ANN) Dense Classification Head
    x = layers.Dense(128, activation="relu", kernel_regularizer=regularizers.l2(l2_reg), name="ann_dense_128")(x)
    x = layers.Dropout(0.30, name="ann_dropout_1")(x)
    x = layers.Dense(64, activation="relu", name="ann_dense_64")(x)
    x = layers.Dropout(0.20, name="ann_dropout_2")(x)
    
    # Output Layer
    outputs = layers.Dense(num_classes, activation="softmax", name="ann_softmax_output")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="AgriVision_CustomCNN")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.TopKCategoricalAccuracy(k=min(3, num_classes), name="top_k_accuracy")]
    )
    
    return model

