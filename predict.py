import numpy as np
import joblib
from tensorflow import keras
import pickle
import joblib
import numpy as np
import tensorflow as tf


def calculate_type(avg_scores):

    # Load the trained model
    model = tf.keras.models.load_model("mbti_predictor.h5")

    # Load the label encoder
    with open("label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)

    # Load the scaler
    scaler_value = joblib.load("scaler.pkl")  # Should be 50.0

    # Example Prediction
    example_input = avg_scores
    # Convert to NumPy array before division

    # example_input_normalized = np.array(example_input) / scaler_value
    # Convert list to NumPy array and reshape it to (1, 5)
    # example_input_normalized = np.array(
    #     avg_scores).reshape(1, 5) / scaler_value
    example_input = np.array([[0, 0, 0, 0, 0]])
    for i in range(5):
        example_input[0][i] = avg_scores[i]
    # example_input_normalized = example_input / scaler_value  # Normalize

    prediction = model.predict(example_input)
    predicted_label = np.argmax(prediction)
    predicted_mbti = label_encoder.inverse_transform([predicted_label])

    print(f"Predicted MBTI Type: {predicted_mbti[0]}")
    return predicted_mbti[0]
