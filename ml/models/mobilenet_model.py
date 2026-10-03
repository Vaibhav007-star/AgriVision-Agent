"""
MobileNetV2 Transfer Learning Model Architecture for AgriVision Agent.
Uses pre-trained ImageNet weights, Depthwise Separable Convolutions, and custom ANN classification head.
"""

from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers, models, applications, regularizers


def build_mobilenetv2_model(
    num_classes: int = 3,
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    fine_tune_layers: int = 20,
    learning_rate: float = 0.0001,
    dropout_rate: float = 0.35,
    l2_reg: float = 0.0001
) -> tf.keras.Model:
    """
    Constructs a Transfer Learning CNN based on MobileNetV2.
    
    Architecture:
    [Input 224x224x3]
         ↓
    [MobileNetV2 Base (ImageNet Weights)]
         ↓
    [GlobalAveragePooling2D]
         ↓
    [BatchNormalization]
         ↓
    [ANN Dense: 256 units, ReLU, L2 Reg]
    [Dropout: dropout_rate]
         ↓
    [ANN Dense: 128 units, ReLU]
    [Dropout: 0.20]
         ↓
    [Softmax Output: num_classes]
    """
    base_model = applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet"
    )
    
    # Freeze base model weights initially
    base_model.trainable = False
    
    # Fine-tuning: Unfreeze top N layers if specified
    if fine_tune_layers > 0:
        base_model.trainable = True
        for layer in base_model.layers[:-fine_tune_layers]:
            layer.trainable = False
            
    inputs = layers.Input(shape=input_shape, name="input_image")
    
    # Feature extraction forward pass
    x = base_model(inputs, training=False)
    
    # Custom ANN Classification Head
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="head_batch_norm")(x)
    x = layers.Dense(256, activation="relu", kernel_regularizer=regularizers.l2(l2_reg), name="ann_dense_256")(x)
    x = layers.Dropout(dropout_rate, name="ann_dropout_1")(x)
    x = layers.Dense(128, activation="relu", name="ann_dense_128")(x)
    x = layers.Dropout(0.20, name="ann_dropout_2")(x)
    
    outputs = layers.Dense(num_classes, activation="softmax", name="ann_softmax_output")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="AgriVision_MobileNetV2")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.TopKCategoricalAccuracy(k=min(3, num_classes), name="top_k_accuracy")]
    )
    
    return model

