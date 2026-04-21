"""
Test Allergy vs Common Cold Disambiguation (Feature #15)

Tests the CRITICAL rule that distinguishes between:
- Allergic Rhinitis (sneezing + runny nose + itching WITHOUT fever)
- Common Cold/Flu (sneezing + runny nose WITH fever)

Rule Priority: ITCHING > sneezing/runny nose
"""

from ai_engine.ai_predictor import AIPredictor
import json

def test_case(name, input_text, expected_disease=None, expected_feature=None):
    """Test case runner for allergy disambiguation"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"INPUT: {input_text}")
    print(f"{'='*80}")
    
    predictor = AIPredictor()
    result = predictor.predict(input_text)
    
    # Extract top prediction
    if result['predictions']:
        top_pred = result['predictions'][0]
        print(f"\nRESULT:")
        print(f"  Disease: {top_pred['disease']}")
        print(f"  Confidence: {top_pred['confidence']}%")
        print(f"  Doctor: {top_pred['doctor']}")
        print(f"  Explanation: {top_pred['explanation']}")
    
    print(f"\nDetected Symptoms: {result['symptoms']}")
    print(f"Severity: {result['severity']}")
    
    # Validate expectations
    if expected_disease and result['predictions']:
        if result['predictions'][0]['disease'] == expected_disease:
            print(f"✓ PASS: Expected disease '{expected_disease}' found")
        else:
            print(f"✗ FAIL: Expected '{expected_disease}', got '{result['predictions'][0]['disease']}'")
    
    if expected_feature and result['predictions']:
        explanation = result['predictions'][0]['explanation'].lower()
        if expected_feature.lower() in explanation:
            print(f"✓ PASS: Explanation contains '{expected_feature}'")
        else:
            print(f"✗ FAIL: Explanation missing '{expected_feature}'")


# ============================================================================
print("\n" + "="*80)
print("ALLERGY vs COMMON COLD DISAMBIGUATION TESTS")
print("="*80)

# Test 1: Classic Allergy - No Fever
print("\n>>> CATEGORY 1: CLEAR ALLERGY (No Fever)")
test_case(
    "Allergy - Itching + Sneezing + Runny Nose (NO FEVER)",
    "I have itching in my eyes and nose, sneezing frequently, and a runny nose",
    expected_disease="Allergic Rhinitis",
    expected_feature="absence of fever"
)

# Test 2: Allergy - Sneezing + Runny Nose + Itching
test_case(
    "Allergy - All symptoms (sneezing, runny nose, itching)",
    "My nose is runny, I keep sneezing, and my eyes are itching",
    expected_disease="Allergic Rhinitis",
    expected_feature="allergy"
)

# Test 3: Cold - Same symptoms but WITH fever
print("\n>>> CATEGORY 2: COMMON COLD/FLU (With Fever)")
test_case(
    "Cold - Fever + Sneezing + Runny Nose (OVERRIDE: allows cold)",
    "I have fever, sneezing, runny nose, and body aches",
    expected_feature="fever"
)

# Test 4: Mild Cold - Slight symptoms with fever
test_case(
    "Cold - Fever with sneezing",
    "I have a fever and I keep sneezing",
    expected_feature="fever"
)

# Test 5: Allergy Only - Just itching and sneezing
print("\n>>> CATEGORY 3: ALLERGY PRIORITY (Itching prioritized)")
test_case(
    "Allergy Priority - Itching + Sneezing (no runny nose mentioned)",
    "My eyes are really itching and I'm sneezing a lot",
    expected_disease="Allergic Rhinitis",
    expected_feature="itching"
)

# Test 6: Allergy - Itching dominant
test_case(
    "Allergy - Itching dominant symptom",
    "I have severe itching in my nose and I'm sneezing",
    expected_disease="Allergic Rhinitis",
    expected_feature="itching"
)

# Test 7: Allergy - Itching + Runny nose (no sneezing mentioned)
test_case(
    "Allergy - Itching + Runny nose",
    "My nose is itching and runny",
    expected_disease="Allergic Rhinitis",
    expected_feature="allergy"
)

# Test 8: Cold - Fever overrides
print("\n>>> CATEGORY 4: FEVER OVERRIDE (Allows Cold/Flu instead)")
test_case(
    "Cold Override - Fever + Itching + Sneezing",
    "I have high fever, itching, and sneezing",
    expected_feature="fever"
)

# Test 9: Cold Override - High fever
test_case(
    "Cold - High fever with runny nose and sneezing",
    "I have a temperature of 101F, runny nose, and sneezing",
    expected_feature="fever"
)

# Test 10: Weak Allergy - Only 1 symptom
print("\n>>> CATEGORY 5: WEAK ALLERGY SIGNALS (Requires 2+ symptoms)")
test_case(
    "Weak Signal - Only sneezing (no itching, no runny nose)",
    "I'm sneezing a lot",
    expected_feature="symptom"
)

# Test 11: Weak Allergy - Only runny nose
test_case(
    "Weak Signal - Only runny nose",
    "My nose is running",
    expected_feature="symptom"
)

# Test 12: Strong Allergy - Itching + multiple symptoms
print("\n>>> CATEGORY 6: STRONG ALLERGY SIGNALS")
test_case(
    "Strong Allergy - Itching + Sneezing + Runny nose + Watery eyes",
    "I have itching in my eyes, lots of sneezing, runny nose, and watery eyes",
    expected_disease="Allergic Rhinitis",
    expected_feature="allergy"
)

# Test 13: Allergy with mild body ache (NO fever)
test_case(
    "Allergy - With body ache but NO fever",
    "I have itching, sneezing, runny nose, and slight body ache (but no fever)",
    expected_disease="Allergic Rhinitis",
    expected_feature="absence of fever"
)

# Test 14: Cold - Body ache + fever (not allergy)
test_case(
    "Cold - Body ache + Fever",
    "I have body aches, fever, and sneezing",
    expected_feature="fever"
)

# Test 15: Allergy vs Cold Comparison
print("\n>>> CATEGORY 7: DISAMBIGUATION EXAMPLES")
test_case(
    "Allergy - Itching is PRIMARY indicator",
    "My eyes are itching terribly, I'm sneezing, and runny nose - but NO fever",
    expected_disease="Allergic Rhinitis",
    expected_feature="itching"
)

test_case(
    "Cold - Fever is PRIMARY indicator",
    "High fever, sneezing, runny nose, and body aches",
    expected_feature="fever"
)

print("\n" + "="*80)
print("ALLERGY vs COMMON COLD DISAMBIGUATION TESTS COMPLETED")
print("="*80)

print("""
✓ TEST EXPECTATIONS:

1. Allergic Rhinitis should be detected when:
   - Has ITCHING (primary rule)
   - Has sneezing and/or runny nose
   - NO FEVER present
   - Confidence: 90%

2. Common Cold/Flu should be suggested when:
   - Has sneezing and/or runny nose
   - HAS FEVER present
   - Fever overrides allergy classification

3. Rule Priority: ITCHING > sneezing/runny nose
   - If itching present (without fever) → Allergy
   - Itching is the key distinguishing factor

4. Weak signals (only 1 symptom) → Not enough for allergy rule
   - Need at least 2 symptoms OR itching + 1 other
""")
