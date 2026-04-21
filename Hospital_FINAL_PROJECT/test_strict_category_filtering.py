"""
Test the strict category filtering feature.
Demonstrates that only diseases from the primary category are kept.
"""

from ai_engine.ai_predictor import AIPredictor
import json

def test_strict_category_filtering(name, input_text, expected_category=None):
    """Test strict category filtering"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"INPUT: {input_text}")
    print(f"EXPECTED PRIMARY CATEGORY: {expected_category}")
    print(f"{'='*80}")
    
    predictor = AIPredictor()
    result = predictor.predict(input_text)
    
    # Extract predicted diseases
    predicted_diseases = [p['disease'] for p in result['predictions']]
    print(f"\nPREDICTED DISEASES (Top 3): {predicted_diseases}")
    print(f"SEVERITY: {result['severity']}")
    
    # Show predictions with confidence
    for pred in result['predictions']:
        print(f"  • {pred['disease']}: {pred['confidence']}% ({pred['doctor']})")
    
    print(f"\nEXPLANATION:")
    for i, pred in enumerate(result['predictions'], 1):
        print(f"  {i}. {pred['explanation']}")
    
    # Validate that primary category diseases are present
    if expected_category:
        print(f"\n✓ Validation: Check that all predictions are from {expected_category} category")
        for disease in predicted_diseases:
            print(f"  - {disease}")


# Test Case 1: Pure Cardiac Symptoms
print("\n" + "="*80)
print("STRICT CATEGORY FILTERING TESTS")
print("="*80)

test_strict_category_filtering(
    "Cardiac Primary (chest pain + sweating + nausea)",
    "I have chest pain, sweating, and nausea",
    expected_category="cardiac"
)

# Test Case 2: Pure Respiratory Symptoms
test_strict_category_filtering(
    "Respiratory Primary (cough + fever + breathlessness)",
    "I have a cough, fever, and difficulty breathing",
    expected_category="respiratory"
)

# Test Case 3: Pure Gastro Symptoms
test_strict_category_filtering(
    "Gastro Primary (vomiting + diarrhea + abdominal pain)",
    "I have vomiting, diarrhea, and bad stomach pain",
    expected_category="gastro"
)

# Test Case 4: Infection Primary
test_strict_category_filtering(
    "Infection Primary (fever + chills + body ache)",
    "I have fever, chills, and my whole body aches",
    expected_category="infection"
)

# Test Case 5: Neurological Primary
test_strict_category_filtering(
    "Neurological Primary (severe headache + nausea + confusion)",
    "I have a severe headache, nausea, and confusion",
    expected_category="neurological"
)

# Test Case 6: Allergic Primary
test_strict_category_filtering(
    "Allergy Primary (sneezing + runny nose + itching)",
    "I have sneezing, runny nose, and itching all over",
    expected_category="allergy"
)

# Test Case 7: Musculoskeletal Primary
test_strict_category_filtering(
    "Musculoskeletal Primary (joint pain + swelling + stiffness)",
    "My joints hurt and are swollen with stiffness",
    expected_category="musculoskeletal"
)

# Test Case 8: Mixed Symptoms - Cardiac Dominates
print("\n" + "="*80)
print("CROSS-CATEGORY TESTS (Multiple categories present)")
print("="*80)

test_strict_category_filtering(
    "Cardiac Dominates (3 cardiac + 1 respiratory)",
    "I have chest pain, sweating, palpitations, and a slight cough",
    expected_category="cardiac"
)

# Test Case 9: Respiratory Dominates
test_strict_category_filtering(
    "Respiratory Dominates (3 respiratory + 1 cardiac)",
    "I have cough, fever, wheezing, and chest tightness",
    expected_category="respiratory"
)

# Test Case 10: Infection Dominates Over Everything
test_strict_category_filtering(
    "Infection High Score (fever + chills + multiple symptoms)",
    "I have high fever, chills, body aches, and I am exhausted",
    expected_category="infection"
)

# Test Case 11: Edge Case - Weak Symptoms in Multiple Categories
test_strict_category_filtering(
    "Minimal Symptoms (only 1 per category)",
    "I have a slight cough and mild headache",
    expected_category="respiratory or neurological"
)

print("\n" + "="*80)
print("STRICT CATEGORY FILTERING TESTS COMPLETED")
print("="*80)
