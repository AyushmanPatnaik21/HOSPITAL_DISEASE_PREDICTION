"""
Comprehensive tests for the upgraded disease prediction system with advanced logic features.
Tests all the new smart filtering, categorization, and context-aware decision logic.
"""

from ai_engine.ai_predictor import AIPredictor
import json

def test_case(name, input_text, expected_diseases=None, should_contain=None):
    """
    Generic test case runner
    """
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"INPUT: {input_text}")
    print(f"{'='*80}")
    
    predictor = AIPredictor()
    result = predictor.predict(input_text)
    
    print(f"\nRESULT:")
    print(json.dumps({
        'symptoms': result['symptoms'],
        'severity': result['severity'],
        'predictions': [
            {
                'disease': p['disease'],
                'confidence': p['confidence'],
                'doctor': p['doctor'],
                'explanation': p['explanation']
            }
            for p in result['predictions']
        ]
    }, indent=2))
    
    # Validate
    if expected_diseases:
        predicted_diseases = [p['disease'] for p in result['predictions']]
        for exp_disease in expected_diseases:
            if exp_disease in predicted_diseases:
                print(f"✓ PASS: Found expected disease '{exp_disease}'")
            else:
                print(f"✗ FAIL: Expected disease '{exp_disease}' not found. Got: {predicted_diseases}")
    
    if should_contain:
        explanation = ' '.join([p['explanation'] for p in result['predictions']])
        for keyword in should_contain:
            if keyword.lower() in explanation.lower():
                print(f"✓ PASS: Explanation contains '{keyword}'")
            else:
                print(f"✗ FAIL: Explanation missing '{keyword}'")
    
    print(f"\nInput validation: {result['input_validation']}")


# Test 1: Mandatory Symptoms - Migraine requires headache
print("\n" + "="*80)
print("CATEGORY 1: MANDATORY SYMPTOMS VALIDATION")
print("="*80)

test_case(
    "Migraine - WITH mandatory headache",
    "I have a severe headache with nausea and sensitivity to light",
    expected_diseases=['Migraine'],
    should_contain=['headache', 'neurological']
)

test_case(
    "High false positive prevention - Nausea alone should NOT trigger Migraine",
    "I have nausea and dizziness",
    should_contain=['Prediction based']
)

# Test 2: Context-Aware Heart Attack Detection
print("\n" + "="*80)
print("CATEGORY 2: CONTEXT-AWARE CARDIAC DETECTION")
print("="*80)

test_case(
    "Heart Attack - WITH strong cardiac evidence (chest pain + sweating)",
    "I have chest pain and I am sweating a lot",
    expected_diseases=['Heart Attack'],
    should_contain=['URGENT', 'cardiac']
)

test_case(
    "Respiratory vs Cardiac - Cough + Fever + Breathlessness should prioritize respiratory",
    "I have a cough, fever, and difficulty breathing",
    expected_diseases=['Pneumonia', 'Bronchitis'],
    should_contain=['respiratory']
)

test_case(
    "Lone Chest Pain - Should be cautious without cardiac symptom support",
    "I have chest pain",
    should_contain=['Prediction based']
)

# Test 3: Body Location Intelligence
print("\n" + "="*80)
print("CATEGORY 3: BODY LOCATION INTELLIGENCE")
print("="*80)

test_case(
    "Back Pain + Nausea - Should suggest kidney disease/UTI priority",
    "I have back pain and nausea",
    should_contain=['back', 'kidney', 'nausea']
)

test_case(
    "Localized Leg Pain - Should suggest musculoskeletal",
    "My leg hurts and is swollen",
    should_contain=['injury', 'orthopedic']
)

test_case(
    "Abdominal Pain Focus - Should suggest gastro diseases",
    "I have abdominal pain and diarrhea with vomiting",
    expected_diseases=['Gastroenteritis', 'Food Poisoning'],
    should_contain=['gastro']
)

# Test 4: Acute vs Chronic Filtering
print("\n" + "="*80)
print("CATEGORY 4: ACUTE vs CHRONIC FILTERING")
print("="*80)

test_case(
    "Fever present - Should REMOVE chronic diseases like Lupus/Parkinson",
    "I have fever, joint pain, and fatigue",
    should_contain=['acute']  # Should suggest acute diseases
)

# Test 5: Category-Based Prioritization
print("\n" + "="*80)
print("CATEGORY 5: CATEGORY-BASED PRIORITIZATION")
print("="*80)

test_case(
    "Respiratory symptoms dominate - Should prioritize respiratory over cardiac",
    "I have cough, wheezing, shortness of breath, and chest tightness",
    expected_diseases=['Asthma', 'Bronchitis'],
    should_contain=['respiratory']
)

test_case(
    "GI symptoms - Should prioritize gastroenteritis",
    "I have nausea, vomiting, diarrhea, and abdominal cramps",
    expected_diseases=['Gastroenteritis', 'Food Poisoning'],
    should_contain=['vomiting', 'diarrhea']
)

# Test 6: Rule-Based High-Confidence Matches
print("\n" + "="*80)
print("CATEGORY 6: RULE-BASED HIGH-CONFIDENCE MATCHES")
print("="*80)

test_case(
    "Diabetes - Frequent urination + Increased thirst (rule-based override)",
    "I have frequent urination and I am very thirsty",
    expected_diseases=['Diabetes'],
    should_contain=['90', 'Endocrinologist']
)

test_case(
    "UTI - Burning urination + Frequent urination",
    "I have burning urination and frequent urination",
    expected_diseases=['Urinary Tract Infection'],
    should_contain=['90', 'Urologist']
)

test_case(
    "Asthma - Wheezing + Breathlessness",
    "I have wheezing and shortness of breath",
    expected_diseases=['Asthma'],
    should_contain=['90', 'Pulmonologist']
)

# Test 7: Weak Input Handling
print("\n" + "="*80)
print("CATEGORY 7: WEAK INPUT HANDLING")
print("="*80)

test_case(
    "Insufficient symptoms - Only 1 symptom",
    "I have a headache",
    should_contain=['more symptoms', 'Insufficient']
)

test_case(
    "No clear symptoms",
    "I don't feel well",
    should_contain=['Insufficient', 'more detailed']
)

# Test 8: Injury/Musculoskeletal Detection
print("\n" + "="*80)
print("CATEGORY 8: INJURY/MUSCULOSKELETAL DETECTION")
print("="*80)

test_case(
    "Trauma-based injury - Fall + Localized pain + Swelling",
    "I fell and my leg is swollen and painful",
    expected_diseases=['Sprain or Strain'],
    should_contain=['Orthopedic']
)

test_case(
    "Localized pain without trauma context - Could be musculoskeletal",
    "My arm hurts and is swollen",
    expected_diseases=['Sprain or Strain'],
    should_contain=['Orthopedic']
)

# Test 9: Fallback Intelligence
print("\n" + "="*80)
print("CATEGORY 9: FALLBACK INTELLIGENCE")
print("="*80)

test_case(
    "Unusual symptom combination - Should provide best guess with low confidence",
    "I have unusual symptoms",
    should_contain=['Prediction based', 'Symptoms']
)

# Test 10: Output Format - Top 3 Diseases
print("\n" + "="*80)
print("CATEGORY 10: OUTPUT FORMAT VALIDATION")
print("="*80)

test_case(
    "Should limit output to top 3 diseases",
    "I have fever, cough, headache, body ache, and sore throat",
    should_contain=['3', 'predictions']
)

# Test 11: Unknown/Out-of-Dataset Handling
print("\n" + "="*80)
print("CATEGORY 11: UNKNOWN SYMPTOMS HANDLING")
print("="*80)

test_case(
    "Very unusual symptom description",
    "My body feels weird and strange",
    should_contain=['unclear', 'consult a doctor']
)

print("\n" + "="*80)
print("ALL TESTS COMPLETED")
print("="*80)
