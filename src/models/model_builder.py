"""
Deep Learning Model Architecture for AgriVision Agent.
Implements Transfer Learning using MobileNetV2 with custom classification head,
fine-tuning capability, and Grad-CAM compatible layer naming.
"""

from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, applications


def build_transfer_learning_model(
    num_classes: int = 15,
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    fine_tune_layers: int = 20,
    learning_rate: float = 1e-4
) -> tf.keras.Model:
    """
    Constructs a Transfer Learning CNN based on MobileNetV2.
    
    Architecture:
    1. MobileNetV2 Base (Pre-trained on ImageNet)
    2. Global Average Pooling 2D
    3. Batch Normalization
    4. Dense Layer (256 units, ReLU) + L2 Regularization
    5. Dropout (0.35)
    6. Dense Layer (128 units, ReLU)
    7. Dropout (0.2)
    8. Softmax Output Layer (num_classes)
    """
    # Base MobileNetV2 without top classifier
    base_model = applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet"
    )
    
    # Freeze base model layers initially
    base_model.trainable = False
    
    # If fine-tuning requested, unfreeze top N layers
    if fine_tune_layers > 0:
        base_model.trainable = True
        for layer in base_model.layers[:-fine_tune_layers]:
            layer.trainable = False
            
    # Input tensor
    inputs = layers.Input(shape=input_shape, name="input_image")
    
    # Forward pass through base feature extractor
    x = base_model(inputs, training=False)
    
    # Custom Dense Classification Head
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="head_batch_norm")(x)
    x = layers.Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4), name="dense_256")(x)
    x = layers.Dropout(0.35, name="dropout_1")(x)
    x = layers.Dense(128, activation="relu", name="dense_128")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)
    
    # Final Softmax prediction layer
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="AgriVision_MobileNetV2")
    
    # Optimizer & Compilation
    optimizer = optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy")
        ]
    )
    
    return model


def get_target_conv_layer(model: tf.keras.Model) -> str:
    """Finds the last 4D convolutional layer name for Grad-CAM."""
    # Look inside base MobileNetV2 if nested
    for layer in reversed(model.layers):
        if hasattr(layer, "layers"): # Sub-model (base MobileNetV2)
            for sub_layer in reversed(layer.layers):
                if isinstance(sub_layer, (layers.Conv2D, layers.DepthwiseConv2D)) or "out_relu" in sub_layer.name or "Conv_1" in sub_layer.name:
                    return sub_layer.name
        elif isinstance(layer, layers.Conv2D):
            return layer.name
    return "out_relu"

