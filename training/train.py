import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical

# Load the dataset
# Replace 'big5_mbti.csv' with the path to your CSV file
data = pd.read_csv("bfpt_mbtidata.csv")

# Display the first few rows to verify the data
print(data.head())

# Select features and target variable
# Assuming the CSV has columns: 'Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'
features = data[['Openness', 'Conscientiousness',
                 'Extraversion', 'Agreeableness', 'Neuroticism']]
labels = data['MBTI_Type']

# Encode the MBTI labels into integers
label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)
# Convert encoded labels into one-hot vectors
labels_onehot = to_categorical(labels_encoded)

# Normalize the feature values
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    features_scaled, labels_onehot, test_size=0.2, random_state=42)

# Build the feed forward neural network model
model = Sequential()
model.add(Dense(64, input_dim=features.shape[1], activation='relu'))
model.add(Dropout(0.2))  # helps reduce overfitting
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.2))
# The output layer: number of neurons equals the number of MBTI types (commonly 16)
model.add(Dense(labels_onehot.shape[1], activation='softmax'))

# Compile the model with categorical crossentropy loss and the Adam optimizer
model.compile(loss='categorical_crossentropy',
              optimizer='adam', metrics=['accuracy'])

# Print model summary
model.summary()

# Train the model
history = model.fit(X_train, y_train, epochs=50,
                    batch_size=32, validation_split=0.2)

# Evaluate the model accuracy loss on the test set
loss, loss2 = model.evaluate(X_test, y_test)
print("Test Loss:", loss)
print("Test Loss:", loss2)


model.save("mbti_model.keras")
print("Model saved to mbti_model.keras")

# Alternatively, if you want to use the legacy HDF5 format, use the .h5 extension:
model.save("mbti_model.h5")
print("Model saved to mbti_model.h5")

joblib.dump(scaler, "scaler.pkl")
print("Scaler saved to scaler.pkl")

joblib.dump(label_encoder, "label_encoder.pkl")
print("Label encoder saved!")
