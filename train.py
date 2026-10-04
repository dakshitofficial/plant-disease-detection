import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image_dataset_from_directory

DATASET_PATH = "dataset/archive/plantvillage dataset/color"

IMG_SIZE = (128, 128)
BATCH_SIZE = 32
SEED = 123
EPOCHS = 2

# Load training dataset
train_ds = image_dataset_from_directory(
    DATASET_PATH,
    validation_split=0.2,
    subset="training",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# Load validation dataset
validation_ds = image_dataset_from_directory(
    DATASET_PATH,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# Class names
class_names = train_ds.class_names

print("\nTotal Classes:", len(class_names))

for i, name in enumerate(class_names):
    print(i, "->", name)

# Optimize dataset
AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(
    buffer_size=AUTOTUNE
)

validation_ds = validation_ds.cache().prefetch(
    buffer_size=AUTOTUNE
)

# CNN model
model = models.Sequential([
    layers.Rescaling(1.0 / 255),

    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Flatten(),

    layers.Dense(128, activation="relu"),
    layers.Dropout(0.5),

    layers.Dense(len(class_names), activation="softmax")
])

# Compile
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Show model
model.summary()

# Training
print("\nStarting training...\n")

history = model.fit(
    train_ds,
    validation_data=validation_ds,
    epochs=EPOCHS
)

# Save model
model.save("plant_disease_model.keras")

print("\n================================")
print("TRAINING COMPLETED!")
print("MODEL SAVED SUCCESSFULLY!")
print("================================")

