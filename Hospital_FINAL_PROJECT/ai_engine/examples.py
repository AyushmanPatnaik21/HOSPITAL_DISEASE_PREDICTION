"""
AI Engine - Usage Examples and Integration Guide

This module demonstrates how to use the upgraded AIPredictor for accurate
disease prediction based on natural language symptom input.
"""

from ai_engine import AIPredictor, get_predictor


# ============================================================================
# EXAMPLE 1: Basic Disease Prediction with Natural Language
# ============================================================================

def example_basic_prediction():
    """Predict disease from natural language symptom input."""
    
    # Initialize predictor
    predictor = get_predictor()
    
    # Example 1: Simple symptom input
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Disease Prediction")
    print("="*70)
    
    user_input = "I have fever and headache"
    result = predictor.predict(user_input)
    
    print(f"\nUser Input: '{user_input}'")
    print(f"Extracted Symptoms: {result['symptoms']}")
    print(f"Severity: {result['severity']}")
    print(f"\nTop 3 Predictions:")
    
    for i, pred in enumerate(result['predictions'], 1):
        print(f"  {i}. {pred['disease']}: {pred['confidence']:.1f}%")
    
    print(f"\nInput Validation: {result['input_validation']}")


# ============================================================================
# EXAMPLE 2: Complex Symptom Input with Multiple Symptoms
# ============================================================================

def example_complex_prediction():
    """Predict from complex multi-symptom input."""
    
    predictor = get_predictor()
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Complex Multi-Symptom Prediction")
    print("="*70)
    
    # Complex input with multiple symptoms
    user_input = "I am having chest pain, shortness of breath, and severe sweating"
    result = predictor.predict(user_input)
    
    print(f"\nUser Input: '{user_input}'")
    print(f"Extracted Symptoms: {result['symptoms']}")
    print(f"Severity: {result['severity']} ⚠️" if result['severity'] == 'High' else f"Severity: {result['severity']}")
    print(f"\nTop 3 Predictions:")
    
    for i, pred in enumerate(result['predictions'], 1):
        doctor = predictor.get_recommended_doctor(pred['disease'])
        print(f"  {i}. {pred['disease']}")
        print(f"     Confidence: {pred['confidence']:.1f}%")
        print(f"     Recommended Doctor: {doctor}")


# ============================================================================
# EXAMPLE 3: Symptom Suggestions (Auto-complete)
# ============================================================================

def example_symptom_suggestions():
    """Get symptom suggestions for autocomplete functionality."""
    
    predictor = get_predictor()
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Symptom Suggestions (Autocomplete)")
    print("="*70)
    
    queries = ["heart", "head", "chest", "fever"]
    
    for query in queries:
        suggestions = predictor.get_symptom_suggestions(query, limit=5)
        print(f"\nQuery: '{query}'")
        print(f"Suggestions: {suggestions}")


# ============================================================================
# EXAMPLE 4: Get All Available Symptoms
# ============================================================================

def example_all_symptoms():
    """Display all available symptoms in the system."""
    
    predictor = get_predictor()
    
    print("\n" + "="*70)
    print("EXAMPLE 4: All Available Symptoms")
    print("="*70)
    
    all_symptoms = predictor.get_all_symptoms()
    
    print(f"\nTotal symptoms available: {len(all_symptoms)}")
    print(f"Symptoms (first 20): {all_symptoms[:20]}")


# ============================================================================
# EXAMPLE 5: Error Handling - Invalid Input
# ============================================================================

def example_error_handling():
    """Handle invalid input gracefully."""
    
    predictor = get_predictor()
    
    print("\n" + "="*70)
    print("EXAMPLE 5: Error Handling")
    print("="*70)
    
    # Test 1: Single symptom (should fail - need at least 2)
    print("\nTest 1: Single symptom input")
    result = predictor.predict("fever")
    print(f"Input: 'fever'")
    print(f"Valid: {result['input_validation']['valid']}")
    print(f"Message: {result['input_validation']['message']}")
    
    # Test 2: Empty input
    print("\nTest 2: Empty input")
    result = predictor.predict("")
    print(f"Input: ''")
    print(f"Valid: {result['input_validation']['valid']}")
    print(f"Message: {result['input_validation']['message']}")
    
    # Test 3: Invalid symptoms
    print("\nTest 3: Invalid symptoms")
    result = predictor.predict("xyz123 abc456")
    print(f"Input: 'xyz123 abc456'")
    print(f"Valid: {result['input_validation']['valid']}")
    print(f"Message: {result['input_validation']['message']}")


# ============================================================================
# EXAMPLE 6: Integration with Flask Routes
# ============================================================================

def example_flask_integration():
    """Example of how to integrate AIPredictor in Flask routes."""
    
    print("\n" + "="*70)
    print("EXAMPLE 6: Flask Integration")
    print("="*70)
    
    # This is how it's used in ml_routes.py:
    code_example = '''
    from ai_engine import AIPredictor
    
    # Initialize at module level
    predictor = AIPredictor()
    
    @app.route('/predict', methods=['POST'])
    def predict():
        user_input = request.form.get('symptoms', '')
        result = predictor.predict(user_input)
        
        if not result['input_validation']['valid']:
            return jsonify({'error': result['input_validation']['message']})
        
        # Get top prediction
        top_pred = result['predictions'][0]
        
        return jsonify({
            'disease': top_pred['disease'],
            'confidence': top_pred['confidence'],
            'severity': result['severity'],
            'predictions': result['predictions']  # Top 3
        })
    '''
    
    print(code_example)


# ============================================================================
# EXAMPLE 7: Severity Detection
# ============================================================================

def example_severity_detection():
    """Demonstrate severity detection for different symptoms."""
    
    predictor = get_predictor()
    
    print("\n" + "="*70)
    print("EXAMPLE 7: Severity Detection")
    print("="*70)
    
    test_cases = [
        ("I have mild cough and runny nose", "Low"),
        ("I have fever and headache", "Medium"),
        ("I have chest pain and shortness of breath", "High"),
        ("I have severe headache and difficulty swallowing", "High"),
    ]
    
    for user_input, expected_severity in test_cases:
        result = predictor.predict(user_input)
        severity = result['severity']
        status = "✓" if severity == expected_severity else "✗"
        
        print(f"\n{status} Input: '{user_input}'")
        print(f"  Expected: {expected_severity}, Got: {severity}")
        print(f"  Symptoms: {result['symptoms']}")


# ============================================================================
# Full Output Format Example
# ============================================================================

def example_output_format():
    """Show complete output format of predictions."""
    
    predictor = get_predictor()
    
    print("\n" + "="*70)
    print("EXAMPLE 8: Complete Output Format")
    print("="*70)
    
    result = predictor.predict("I have fever, cough, and fatigue")
    
    print("\nFull JSON Response Structure:")
    print("{")
    print(f"  'symptoms': {result['symptoms']},")
    print(f"  'severity': '{result['severity']}',")
    print(f"  'predictions': [")
    
    for i, pred in enumerate(result['predictions']):
        print(f"    {i}: {{")
        print(f"      'disease': '{pred['disease']}',")
        print(f"      'confidence': {pred['confidence']}")
        print(f"    }}" + ("," if i < len(result['predictions'])-1 else ""))
    
    print(f"  ],")
    print(f"  'input_validation': {{")
    print(f"    'valid': {result['input_validation']['valid']},")
    print(f"    'message': \"{result['input_validation']['message']}\"")
    print(f"  }}")
    print("}")


# ============================================================================
# Run All Examples
# ============================================================================

if __name__ == "__main__":
    try:
        print("\n" + "#"*70)
        print("# AI PREDICTOR - USAGE EXAMPLES")
        print("#"*70)
        
        example_basic_prediction()
        example_complex_prediction()
        example_symptom_suggestions()
        example_all_symptoms()
        example_error_handling()
        example_severity_detection()
        example_output_format()
        example_flask_integration()
        
        print("\n" + "#"*70)
        print("# ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("#"*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
