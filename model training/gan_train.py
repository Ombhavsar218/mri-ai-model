import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing.image import img_to_array, load_img

# --- Step 1: Prepare the Dataset ---
dataset_dir = "D:/Final Project/Brain_Tumor"

def load_images(dataset_dir, target_size=(64, 64)):
    images = []
    labels = []
    classes = os.listdir(os.path.join(dataset_dir, "Training"))
    class_dict = {cls: idx for idx, cls in enumerate(classes)}  # Assign an index to each class
    for cls in classes:
        class_folder = os.path.join(dataset_dir, "Training", cls)
        for img_name in os.listdir(class_folder):
            img_path = os.path.join(class_folder, img_name)
            img = load_img(img_path, target_size=target_size)
            img_array = img_to_array(img) / 127.5 - 1.0  # Normalize to [-1, 1]
            images.append(img_array)
            labels.append(class_dict[cls])  # Add the corresponding label
    return np.array(images), np.array(labels)

# Load the images
print("Loading images...")
images, labels = load_images(dataset_dir)
print(f"Loaded {images.shape[0]} images of shape {images.shape[1:]}.")

# --- Step 2: Define the Generator ---
def build_generator(latent_dim):
    model = models.Sequential()
    model.add(layers.Dense(256 * 8 * 8, input_dim=latent_dim))
    model.add(layers.Reshape((8, 8, 256)))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2DTranspose(128, kernel_size=4, strides=2, padding='same', activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2DTranspose(64, kernel_size=4, strides=2, padding='same', activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2DTranspose(3, kernel_size=4, strides=2, padding='same', activation='tanh'))  # Output 3-channel image
    return model

latent_dim = 100
generator = build_generator(latent_dim)
generator.summary()

# --- Step 3: Define the Discriminator ---
def build_discriminator(input_shape=(64, 64, 3)):
    model = models.Sequential()
    model.add(layers.Conv2D(64, kernel_size=4, strides=2, padding='same', input_shape=input_shape))
    model.add(layers.LeakyReLU(alpha=0.2))
    model.add(layers.Dropout(0.3))
    model.add(layers.Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(layers.LeakyReLU(alpha=0.2))
    model.add(layers.Dropout(0.3))
    model.add(layers.Flatten())
    model.add(layers.Dense(1, activation='sigmoid'))
    return model

# Ensure discriminator is compiled correctly
discriminator = build_discriminator()
discriminator.compile(optimizer=optimizers.Adam(learning_rate=0.0002, beta_1=0.5), 
                      loss='binary_crossentropy', 
                      metrics=['accuracy'])

# --- Step 4: Define the GAN ---
def build_gan(generator, discriminator):
    # Make the discriminator untrainable for the GAN model
    discriminator.trainable = False
    model = models.Sequential([generator, discriminator])
    return model

gan = build_gan(generator, discriminator)

# Compile GAN model with binary cross entropy loss for generator optimization
gan.compile(optimizer=optimizers.Adam(learning_rate=0.0002, beta_1=0.5), 
            loss='binary_crossentropy')

# --- Step 5: Train the GAN ---
def train_gan(generator, discriminator, gan, dataset, latent_dim, epochs=10000, batch_size=64, save_interval=1000):
    valid = np.ones((batch_size, 1))  # Real images
    fake = np.zeros((batch_size, 1))  # Fake images

    for epoch in range(epochs):
        # --- Train the Discriminator ---
        idx = np.random.randint(0, dataset.shape[0], batch_size)
        real_images = dataset[idx]

        # Generate fake images
        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        fake_images = generator.predict(noise)

        # Train the discriminator (real and fake images)
        d_loss_real = discriminator.train_on_batch(real_images, valid)
        d_loss_fake = discriminator.train_on_batch(fake_images, fake)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

        # --- Train the Generator ---
        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        g_loss = gan.train_on_batch(noise, valid)  # The generator wants the discriminator to classify generated images as real

        # Print progress
        print(f"{epoch + 1}/{epochs} [D loss: {d_loss[0]:.4f}, acc.: {100 * d_loss[1]:.2f}%] [G loss: {g_loss:.4f}]")

        # Save generated images at save intervals
        if (epoch + 1) % save_interval == 0:
            save_generated_images(generator, latent_dim, epoch + 1)

    # Save the generator and discriminator models after training
    generator.save("D:/Final Project/Brain_Tumor_Generator.h5")
    print("Generator model saved at: D:/Final Project/Brain_Tumor_Generator.h5")
    discriminator.save("D:/Final Project/Brain_Tumor_Discriminator.h5")
    print("Discriminator model saved at: D:/Final Project/Brain_Tumor_Discriminator.h5")

# Function to save generated images
def save_generated_images(generator, latent_dim, epoch, examples=25, save_path="generated_images"):
    os.makedirs(save_path, exist_ok=True)
    noise = np.random.normal(0, 1, (examples, latent_dim))
    generated_images = generator.predict(noise)
    generated_images = (generated_images + 1) / 2.0  # Rescale to [0, 1]

    plt.figure(figsize=(10, 10))
    for i in range(examples):
        plt.subplot(5, 5, i + 1)
        plt.imshow(generated_images[i])
        plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"{save_path}/epoch_{epoch}.png")
    print(f"Saved generated images at epoch {epoch}.")

# Train the GAN
train_gan(generator, discriminator, gan, images, latent_dim, epochs=10000, batch_size=32, save_interval=1000)
