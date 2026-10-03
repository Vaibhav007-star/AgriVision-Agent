"""
================================================================================
🌾 AgriVision Agent — Deep Learning & Artificial Neural Network (ANN) Module
================================================================================
Academic Subject: Artificial Neural Networks (ANN) & Deep Learning

This module implements two distinct neural architectures:
1. Custom Baseline CNN (Classical Multi-Layer Feature Extractor + Dense ANN Head)
2. Transfer Learning Model based on MobileNetV2 (Depthwise Separable Convolutions + Dense ANN Head)

--------------------------------------------------------------------------------
ANN / CNN Integration Theory & Layer Breakdown:
--------------------------------------------------------------------------------
A standard Computer Vision classification pipeline is fundamentally a hybrid system:
- The Convolutional Neural Network (CNN) acts as a specialized spatial feature extractor.
  It transforms raw pixel arrays into high-level spatial representations (edges, textures, lesion rings).
- The Artificial Neural Network (ANN) dense layers act as the universal decision maker.
  It learns non-linear decision boundaries over the extracted feature embeddings.

Data Flow Pipeline:
  [Input Leaf Image: 224 x 224 x 3]
              ↓
  [CNN Feature Extraction Backbone]
  (Conv2D + Batch Normalization + ReLU Activation + MaxPooling2D)
              ↓
  [Spatial Tensor: e.g. 7 x 7 x 1280]
              ↓
  [Global Average Pooling 2D (GAP2D)]
  (Collapses 2D spatial dimensions to a 1D Feature Vector: 1280-dim)
              ↓
  [ANN Hidden Dense Layer 1: 256 Neurons, ReLU Activation, L2 Regularization]
  [ANN Dropout Regularization: rate = 0.35 (prevents co-adaptation / overfitting)]
              ↓
  [ANN Hidden Dense Layer 2: 128 Neurons, ReLU Activation]
  [ANN Dropout Regularization: rate = 0.20]
              ↓
  [ANN Output Layer: Dense(num_classes) with Softmax Activation]
  (Outputs normalized posterior class probability distribution: sum(P) = 1.0)
================================================================================
"""

from typing import Tuple, Dict, Any, Optional
import tensorflow as tf
from tensorflow.keras import layers, models, applications, regularizers


def build_custom_cnn(
    num_classes: int = 3,
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    learning_rate: float = 0.0005,
    l2_reg: float = 0.0001
) -> tf.keras.Model:
    """
    Constructs a classical Convolutional Neural Network with an ANN classification head.
    
    Layer-by-Layer Architecture:
    1. Input Layer: Accepts RGB images of dimensions (224, 224, 3).
    2. Conv Block 1: 32 filters (3x3), ReLU activation, Batch Normalization, MaxPool2D(2,2).
    3. Conv Block 2: 64 filters (3x3), ReLU activation, Batch Normalization, MaxPool2D(2,2).
    4. Conv Block 3: 128 filters (3x3), ReLU activation, Batch Normalization, MaxPool2D(2,2).
    5. Feature Pooling: GlobalAveragePooling2D collapses spatial maps into a compact feature vector.
    6. ANN Dense Layer 1: 128 fully connected neurons with ReLU and L2 weight decay.
    7. ANN Dropout 1: Discards 30% of activations during training to avoid overfitting.
    8. ANN Dense Layer 2: 64 fully connected neurons with ReLU.
    9. ANN Dropout 2: Discards 20% of activations.
    10. Output Softmax Layer: Outputs class probabilities for all target crop conditions.
    """
    inputs = layers.Input(shape=input_shape, name="raw_input_image")
    
    # --- CNN Feature Extractor ---
    # Block 1: Low-level spatial features (edges, color boundaries)
    x = layers.Conv2D(32, (3, 3), padding="same", activation="relu", name="conv_block1_conv")(inputs)
    x = layers.BatchNormalization(name="conv_block1_bn")(x)
    x = layers.MaxPooling2D((2, 2), name="conv_block1_pool")(x)
    
    # Block 2: Mid-level textural features (leaf veins, spots, discoloration)
    x = layers.Conv2D(64, (3, 3), padding="same", activation="relu", name="conv_block2_conv")(x)
    x = layers.BatchNormalization(name="conv_block2_bn")(x)
    x = layers.MaxPooling2D((2, 2), name="conv_block2_pool")(x)
    
    # Block 3: High-level pathological patterns (necrotic concentric rings, blotches)
    x = layers.Conv2D(128, (3, 3), padding="same", activation="relu", name="conv_block3_conv")(x)
    x = layers.BatchNormalization(name="conv_block3_bn")(x)
    x = layers.MaxPooling2D((2, 2), name="conv_block3_pool")(x)
    
    # Spatial Dimensionality Reduction
    x = layers.GlobalAveragePooling2D(name="gap2d_feature_vector")(x)
    
    # --- Artificial Neural Network (ANN) Classifier ---
    # Hidden Layer 1
    x = layers.Dense(
        128,
        activation="relu",
        kernel_regularizer=regularizers.l2(l2_reg),
        name="ann_hidden_dense_128"
    )(x)
    x = layers.Dropout(0.30, name="ann_dropout_1")(x)
    
    # Hidden Layer 2
    x = layers.Dense(64, activation="relu", name="ann_hidden_dense_64")(x)
    x = layers.Dropout(0.20, name="ann_dropout_2")(x)
    
    # Softmax Classification Output Layer
    outputs = layers.Dense(num_classes, activation="softmax", name="ann_softmax_probabilities")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="AgriVision_Custom_CNN")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.TopKCategoricalAccuracy(k=min(3, num_classes), name="top_k_acc")]
    )
    
    return model


def build_mobilenet_transfer_model(
    num_classes: int = 3,
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    fine_tune_layers: int = 20,
    learning_rate: float = 0.0001,
    dropout_rate: float = 0.35,
    l2_reg: float = 0.0001
) -> tf.keras.Model:
    """
    Constructs a Transfer Learning architecture using pre-trained MobileNetV2 as feature backbone.
    
    Key Architectural Innovations:
    1. Depthwise Separable Convolutions: Reduces multiply-accumulate operations by ~8-9x vs standard CNNs.
    2. Inverted Residual Bottlenecks: Expands to higher dimension, filters depthwise, and projects back with linear bottleneck.
    3. Transfer Learning: Leverages millions of generalized visual weights trained on ImageNet.
    4. Custom Dense ANN Head: Specifically fine-tuned on agricultural crop pathology.
    """
    base_model = applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet"
    )
    
    # Freeze lower feature extractor layers
    base_model.trainable = False
    
    if fine_tune_layers > 0:
        base_model.trainable = True
        for layer in base_model.layers[:-fine_tune_layers]:
            layer.trainable = False
            
    inputs = layers.Input(shape=input_shape, name="input_leaf_tensor")
    
    # Forward pass through pre-trained backbone
    x = base_model(inputs, training=False)
    
    # ANN Dense Head
    x = layers.GlobalAveragePooling2D(name="gap2d_pooling")(x)
    x = layers.BatchNormalization(name="ann_head_bn")(x)
    
    # Dense Hidden Layer 1
    x = layers.Dense(
        256,
        activation="relu",
        kernel_regularizer=regularizers.l2(l2_reg),
        name="ann_dense_256"
    )(x)
    x = layers.Dropout(dropout_rate, name="ann_dropout_1")(x)
    
    # Dense Hidden Layer 2
    x = layers.Dense(128, activation="relu", name="ann_dense_128")(x)
    x = layers.Dropout(0.20, name="ann_dropout_2")(x)
    
    # Output Softmax Layer
    outputs = layers.Dense(num_classes, activation="softmax", name="ann_softmax_output")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="AgriVision_MobileNetV2_Transfer")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.TopKCategoricalAccuracy(k=min(3, num_classes), name="top_k_acc")]
    )
    
    return model

