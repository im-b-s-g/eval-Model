import numpy as np
import joblib
from tensorflow import keras

# Load the trained model
model = keras.models.load_model("./Evaluation model/mbti_model.h5")
print("Model loaded successfully!")

# Load the saved scaler
scaler = joblib.load("scaler.pkl")
print("Scaler loaded successfully!")

# Define the Big Five personality traits
traits = ['Openness', 'Conscientiousness',
          'Extraversion', 'Agreeableness', 'Neuroticism']

# Get user input for each trait
input_values = []
print("Enter the Big 5 trait values (0.0 to 1.0):")
for trait in traits:
    try:
        value = float(input(f"{trait}: "))
        input_values.append(value)
    except ValueError:
        print(f"Invalid input for {trait}. Please enter a numeric value.")
        exit()

# Convert input list to NumPy array and reshape for a single sample
input_array = np.array(input_values).reshape(1, -1)

# Scale the input using the same scaler from training
input_array_scaled = scaler.transform(input_array)

# Predict using the trained model
predicted_probs = model.predict(input_array_scaled)

# Get the class with the highest probability
predicted_class = np.argmax(predicted_probs, axis=1)

# Load label encoder and decode the predicted class index
label_encoder = joblib.load("label_encoder.pkl")
predicted_mbti = label_encoder.inverse_transform(predicted_class)

print("Predicted MBTI type:", predicted_mbti[0])
