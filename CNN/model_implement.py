import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Only show errors
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

IMG_SIZE = 128  # Must match training

def load_and_preprocess_local_image(img_path):
    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

def predict_image(model_path, img_path):
    model = tf.keras.models.load_model(model_path)
    img_array = load_and_preprocess_local_image(img_path)
    prediction = model.predict(img_array)
    if prediction[0][0] > 0.5:
        print("Prediction: Dog")
    else:
        print("Prediction: Cat")

if __name__ == "__main__":
    """ import sys
    if len(sys.argv) != 3:
        print("Usage: python predict_cat_dog.py <model_path> <image_path>")
        sys.exit(1)
    model_path = sys.argv[1]
    img_path = sys.argv[2] """ 
    model_path = "cat_dog_model.keras"  # Replace with your model path
    img_path = "cat1.jpeg"  # Replace with your image path
    predict_image(model_path, img_path)