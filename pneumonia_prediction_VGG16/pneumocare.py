import streamlit as st
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import VGG16, decode_predictions

# Load the VGG16 model
model = load_model('lung_vgg16.h5')

def preprocess_image(img):
    # Resize image to the input size expected by VGG16 (224x224 pixels)
    img = img.resize((224, 224))
    
    # Convert the image to RGB
    img = img.convert('RGB')
    
    # Convert the image to a NumPy array
    img_array = image.img_to_array(img)

    # Add an extra dimension and preprocess the image
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    return img_array

def perform_inference(processed_image, model):
    # Perform inference
    predictions = model.predict(processed_image)
    
    return predictions

# Streamlit app
def main():
    st.title("PneumoCare AI")

    # Upload image through Streamlit
    uploaded_image = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_image:
        # Display the uploaded image
        st.image(uploaded_image, use_column_width=True, caption="Uploaded Image")

        # Process the image
        processed_image = preprocess_image(Image.open(uploaded_image))
        
        # Model inference
        model_output = perform_inference(processed_image, model)

        # Display model output
        st.text(f"Model Output: {model_output}")

        # Determine the predicted class based on the highest probability
        predicted_class = "Pneumonia Confirmed" if model_output[0, 1] > model_output[0, 0] else "Normal patient"

        # Display the final prediction
        st.text(f"Final Prediction: {predicted_class}")

if __name__ == "__main__":
    main()