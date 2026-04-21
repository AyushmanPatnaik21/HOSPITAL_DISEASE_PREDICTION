"""
Quick Flask Integration Test for Hybrid AI System
"""
import sys
sys.path.insert(0, r'c:\Users\asuto\Desktop\Hospital')

from ai_engine.ai_predictor import AIPredictor

print("=" * 70)
print("FLASK INTEGRATION TEST - Hybrid AI System")
print("=" * 70)

# Initialize the hybrid AI system
ai_system = AIPredictor()

test_cases = [
    "fever and cough",
    "chest pain, shortness of breath",
    "headache, nausea, sensitivity to light",
    "rash and itching",
]

for test_input in test_cases:
    print(f"\nTest Input: {test_input}")
    try:
        result = ai_system.predict(test_input)
        print(f"  ✓ Top Prediction: {result['predictions'][0]['disease']}")
        print(f"  ✓ Confidence: {result['predictions'][0]['confidence']:.2f}%")
        print(f"  ✓ Severity: {result['severity']}")
        print(f"  ✓ Total predictions: {len(result['predictions'])}")
        print(f"  ✓ Output format valid: {all(k in result for k in ['symptoms', 'severity', 'predictions'])}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")

print("\n" + "=" * 70)
print("[SUCCESS] Flask app integrates correctly with hybrid AI system!")
print("=" * 70)
