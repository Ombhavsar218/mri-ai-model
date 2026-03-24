import os
import cv2
import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from tensorflow.keras.applications import VGG16
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Use a non-interactive backend to avoid pop-ups
matplotlib.use('Agg')

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# --- Check GPU Availability ---
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

# Clear any previous session to free up memory
tf.keras.backend.clear_session()

# Define dataset directory
dataset_dir = "D:/Final Project/Brain_Tumor"  # Update the path as needed

# Define classes based on folder names
classes = ["pituitary", "notumor", "meningioma", "glioma"]

# Function to load and visualize a few sample images from each class
def visualize_dataset(dataset_dir, classes, num_images=5, save_path="dataset_visualization.png"):
    plt.figure(figsize=(15, 10))
    
    for idx, cls in enumerate(classes):
        cls_folder = os.path.join(dataset_dir, "Training", cls)  # Adjust path for training data
        if not os.path.exists(cls_folder):
            print(f"Folder not found: {cls_folder}")  # Added check to ensure folder exists
            continue
        
        images = os.listdir(cls_folder)[:num_images]  # Get a few sample images
        for i, img_name in enumerate(images):
            img_path = os.path.join(cls_folder, img_name)
            img = cv2.imread(img_path)  # Read image using OpenCV
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            
            # Plot image
            plt.subplot(len(classes), num_images, idx * num_images + i + 1)
            plt.imshow(img)
            plt.axis('off')
            plt.title(cls)
    
    plt.tight_layout()
    plt.savefig(save_path)  # Save the figure instead of showing
    print(f"Visualization saved to {save_path}")

# Visualize the dataset
visualize_dataset(dataset_dir, classes)

# --- Image Preprocessing (Normalization & Augmentation) ---
# Create ImageDataGenerator for data augmentation and normalization
datagen = ImageDataGenerator(
    rescale=1.0/255.0,  # Normalize pixel values to be between 0 and 1
    rotation_range=40,  # Random rotations between 0 and 40 degrees
    width_shift_range=0.2,  # Random horizontal shifts
    height_shift_range=0.2,  # Random vertical shifts
    shear_range=0.2,  # Random shear transformations
    zoom_range=0.2,  # Random zooming
    horizontal_flip=True,  # Random horizontal flipping
    fill_mode='nearest'  # Fill pixels after transformations
)

# Set up ImageDataGenerator for training and testing
batch_size = 16  # Reduced batch size for lower memory usage

train_datagen = datagen.flow_from_directory(
    'D:/Final Project/Brain_Tumor/Training',  # Training data path
    target_size=(224, 224),  # Resize images to 224x224 (adjust as needed)
    batch_size=batch_size,  # Batch size
    class_mode='categorical',  # Multi-class classification
)

test_datagen = ImageDataGenerator(rescale=1.0/255.0)  # Only rescale for testing

test_datagen = test_datagen.flow_from_directory(
    'D:/Final Project/Brain_Tumor/Testing',  # Testing data path
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode='categorical',
)

# Example: Print out the class names
print(f"Class names: {train_datagen.class_indices}")

# --- Step 2: Build the CNN Model with Transfer Learning ---
# Load VGG16 pre-trained model without the top classification layer
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze the base model layers

# Build the model
model = models.Sequential([
    base_model,  # Use the pre-trained VGG16 model
    layers.GlobalAveragePooling2D(),  # Global average pooling for better feature extraction
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),  # Dropout layer for regularization
    layers.Dense(4, activation='softmax')  # Output layer for 4 classes
])

# Summary of the model
model.summary()

# Compile the model
model.compile(
    optimizer='adam',  # Optimizer
    loss='categorical_crossentropy',  # Loss function for multi-class classification
    metrics=['accuracy']  # Metrics to track
)

# --- Step 3: Train the Model with Callbacks ---
# Early Stopping to prevent overfitting
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Reduce learning rate on plateau
lr_reduction = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)

# Train the model
history = model.fit(
    train_datagen,  # Training data generator
    steps_per_epoch=train_datagen.samples // train_datagen.batch_size,  # Steps per epoch
    epochs=20,  # Number of epochs (increase for more training)
    validation_data=test_datagen,  # Validation data generator
    validation_steps=test_datagen.samples // test_datagen.batch_size,  # Validation steps
    callbacks=[early_stopping, lr_reduction]  # Callbacks to improve performance
)

# --- Step 4: Evaluate the Model ---
# Evaluate the model on the test set
test_loss, test_accuracy = model.evaluate(test_datagen)
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")

# --- Step 5: Save the Model ---
# Save the entire model
model_save_path = "D:/Final Project/Brain_Tumor_Model.h5"
model.save(model_save_path)
print(f"Model saved to {model_save_path}")
