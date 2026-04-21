"""ML controller - Business logic for machine learning predictions"""
from flask import request, jsonify
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_engine.ai_predictor import AIPredictor

# Initialize the hybrid AI system
ai_system = AIPredictor()

def predict_disease():
    """Predict disease based on symptoms using hybrid AI system"""
    try:
        data = request.get_json()
        symptoms_str = data.get('symptoms', '')
        
        # Use the hybrid AI predictor
        result = ai_system.predict(symptoms_str)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


