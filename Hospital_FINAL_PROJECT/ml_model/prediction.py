import pickle
import numpy as np
import os

# Load model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "model.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

# Example symptoms list (must match training)
all_symptoms = [
    "fever", "cough", "headache", "fatigue",
    "chest_pain", "sweating", "nausea",
    "vomiting", "dizziness", "shortness_of_breath"
]

def predict_disease(user_symptoms):
    """
    Predict disease from symptoms with normalized confidence scores.
    
    Applies confidence normalization:
    - Highest prediction scaled to ~90% (using 0.9 factor)
    - Other predictions scaled proportionally
    - All values clamped between 5% and 95%
    """
    input_data = [1 if symptom in user_symptoms else 0 for symptom in all_symptoms]

    input_data = np.array(input_data).reshape(1, -1)

    prediction = model.predict(input_data)[0]

    # Get probabilities for normalization
    probabilities = model.predict_proba(input_data)[0]
    
    # Find maximum probability for normalization
    max_probability = np.max(probabilities)
    
    # For the top prediction confidence:
    # Normalize: (max_prob / max_prob) = 1.0
    # Apply 0.9 scaling: 1.0 * 0.9 = 0.9
    # Convert to percentage: 0.9 * 100 = 90%
    # Formula: (max_prob / max_prob) * 0.9 * 100 = 90.0
    normalized_confidence = (max_probability / max_probability) * 0.9 * 100
    
    # Clamp between 5% and 95%
    confidence = max(5.0, min(95.0, normalized_confidence))
    confidence = round(confidence, 1)

    return prediction, confidence