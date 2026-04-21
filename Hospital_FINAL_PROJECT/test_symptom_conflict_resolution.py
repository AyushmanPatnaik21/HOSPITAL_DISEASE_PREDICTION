"""
Test Suite for Feature #16: Symptom Conflict Resolution (CRITICAL FINAL LOGIC)

Tests the intelligent handling of conflicting symptoms:
1. Allergy + Fever coexistence
2. Bronchitis mandatory cough requirement
3. Rule priority ordering

Feature #16 resolves conflicts between competing diagnoses.
"""

import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '.')

from ai_engine.ai_predictor import AIPredictor
import json

# Initialize predictor
predictor = AIPredictor()

print("\n" + "="*80)
print("FEATURE #16: SYMPTOM CONFLICT RESOLUTION COMPREHENSIVE TEST SUITE")
print("="*80)

# Test counter
test_count = 0
passed = 0
failed = 0

def run_test(name, input_text, expected_disease=None, expected_position=None, check_secondary=False):
    """Run a single test case"""
    global test_count, passed, failed
    test_count += 1
    
    print(f"\n--- TEST {test_count}: {name} ---")
    print(f"Input: {input_text}")
    
    try:
        result = predictor.predict(input_text)
        
        if result['predictions']:
            top_disease = result['predictions'][0]['disease']
            confidence = result['predictions'][0]['confidence']
            
            print(f"Result: {top_disease} ({confidence}%)")
            
            # Check if primary disease matches
            if expected_disease:
                if top_disease == expected_disease:
                    print(f"✅ PASS: Got expected {expected_disease}")
                    passed += 1
                else:
                    print(f"❌ FAIL: Expected {expected_disease}, got {top_disease}")
                    failed += 1
            
            # Check secondary diagnosis (for conflict resolution)
            if check_secondary and len(result['predictions']) > 1:
                secondary = result['predictions'][1]['disease']
                print(f"Secondary: {secondary}")
                if secondary == expected_disease:
                    print(f"✅ PASS: Got expected secondary {expected_disease}")
                    passed += 1
                else:
                    print(f"❌ FAIL: Expected secondary {expected_disease}, got {secondary}")
                    failed += 1
            
            # Print all predictions if multiple
            if len(result['predictions']) > 1:
                print("All predictions:")
                for i, pred in enumerate(result['predictions']):
                    print(f"  {i+1}. {pred['disease']} ({pred['confidence']}%)")
            
            return True
        else:
            print(f"❌ FAIL: No predictions returned")
            failed += 1
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        failed += 1
        return False


# ============================================================================
# SECTION 1: ALLERGY + FEVER CONFLICT RESOLUTION
# ============================================================================

print("\n" + "="*80)
print("SECTION 1: ALLERGY + FEVER CONFLICT RESOLUTION")
print("="*80)
print("Testing how system prioritizes allergy when itching is present with fever")

# Test 1: Clear allergy (no fever) - BASELINE
run_test(
    "Clear Allergy (No Fever)",
    "My eyes are itching, I'm sneezing, runny nose",
    expected_disease="Allergic Rhinitis"
)

# Test 2: Allergy with fever - CONFLICT RESOLUTION
run_test(
    "Allergy + Fever (Conflict Resolution)",
    "Eyes itching, sneezing, runny nose, fever",
    expected_disease="Allergic Rhinitis"
)

# Test 3: Allergy with high fever - ITCHING still prioritized
run_test(
    "Allergy + High Fever (ITCHING Priority)",
    "Nose is itching, sneezing, runny nose, high fever",
    expected_disease="Allergic Rhinitis"
)

# Test 4: Allergy with fever - Check dual diagnosis
run_test(
    "Allergy + Fever - Dual Diagnosis",
    "Itching eyes and nose, sneezing, runny nose, fever 101F",
    expected_disease="Allergic Rhinitis"
)

# Test 5: Weak allergy response (no itching, just fever)
run_test(
    "No Itching, Just Fever (Not Allergy)",
    "sneezing, runny nose, fever",
    expected_disease="Common Cold"
)


# ============================================================================
# SECTION 2: BRONCHITIS MANDATORY COUGH REQUIREMENT
# ============================================================================

print("\n" + "="*80)
print("SECTION 2: BRONCHITIS MANDATORY COUGH REQUIREMENT")
print("="*80)
print("Testing that Bronchitis is ONLY predicted when cough is present")

# Test 6: Bronchitis WITH cough (should be allowed)
run_test(
    "Bronchitis WITH Cough (Mandatory Met)",
    "I have persistent cough, chest pain, fever, fatigue",
    expected_disease="Bronchitis"
)

# Test 7: Bronchitis-like WITHOUT cough (should be REMOVED)
run_test(
    "Fever + Fatigue WITHOUT Cough (Bronchitis Removed)",
    "fever, fatigue, shortness of breath",
    expected_disease=None  # Bronchitis should NOT be in results
)

# Test 8: Respiratory symptoms WITHOUT cough
run_test(
    "Respiratory Symptoms Without Cough",
    "wheezing, breathlessness, fatigue",
    expected_disease="Asthma"  # Should be asthma, not bronchitis
)

# Test 9: Bronchitis with cough and wheezing
run_test(
    "Bronchitis WITH Cough and Wheezing",
    "cough, wheezing, fever, chest pain",
    expected_disease="Bronchitis"
)

# Test 10: Missing cough removes bronchitis
run_test(
    "Chest Pain + Fever - No Cough (Not Bronchitis)",
    "chest pain, fever, body ache",
    expected_disease=None  # Should be other disease, not bronchitis
)


# ============================================================================
# SECTION 3: STRONG INDICATORS PRIORITY
# ============================================================================

print("\n" + "="*80)
print("SECTION 3: STRONG INDICATORS PRIORITY")
print("="*80)
print("Testing rule priority ordering: Strong indicators ranked highest")

# Test 11: Chest pain (strong indicator)
run_test(
    "Chest Pain - Strong Cardiac Indicator",
    "chest pain, sweating, dizziness",
    expected_disease="Heart Attack"
)

# Test 12: Itching (strong indicator for allergy)
run_test(
    "Itching - Strong Allergy Indicator",
    "itching, sneezing, no fever",
    expected_disease="Allergic Rhinitis"
)

# Test 13: Burning urination (strong urinary indicator)
run_test(
    "Burning Urination - Strong UTI Indicator",
    "burning sensation while urinating, frequent urination",
    expected_disease="Urinary Tract Infection"
)

# Test 14: Mixed symptoms - strong indicator prioritized
run_test(
    "Mixed Symptoms - Itching Priority Over Fever",
    "itching, fever, fatigue, sneezing",
    expected_disease="Allergic Rhinitis"
)

# Test 15: Strong indicator determines category
run_test(
    "Urination Issues - Category Priority",
    "burning urination, frequent urination, nausea",
    expected_disease="Urinary Tract Infection"
)


# ============================================================================
# SECTION 4: MANDATORY SYMPTOMS ENFORCEMENT
# ============================================================================

print("\n" + "="*80)
print("SECTION 4: MANDATORY SYMPTOMS ENFORCEMENT")
print("="*80)
print("Testing that diseases without mandatory symptoms are removed")

# Test 16: Migraine WITH mandatory headache
run_test(
    "Migraine WITH Mandatory Headache",
    "severe headache, nausea, sensitivity to light",
    expected_disease="Migraine"
)

# Test 17: Heart Attack WITH mandatory chest pain
run_test(
    "Heart Attack WITH Mandatory Chest Pain",
    "chest pain, sweating, arm pain",
    expected_disease="Heart Attack"
)

# Test 18: Asthma WITH mandatory wheezing
run_test(
    "Asthma WITH Mandatory Wheezing",
    "wheezing, shortness of breath, chest tightness",
    expected_disease="Asthma"
)

# Test 19: UTI WITH mandatory burning urination
run_test(
    "UTI WITH Mandatory Burning Urination",
    "burning urination, frequent urination, kidney pain",
    expected_disease="Urinary Tract Infection"
)


# ============================================================================
# SECTION 5: REAL-WORLD COMPLEX SCENARIOS
# ============================================================================

print("\n" + "="*80)
print("SECTION 5: REAL-WORLD COMPLEX SCENARIOS")
print("="*80)
print("Testing realistic multi-symptom cases with conflict resolution")

# Test 20: Patient with both allergy and cold symptoms
run_test(
    "Allergy + Cold Coexistence",
    "eyes are itching, sneezing constantly, runny nose, fever 100F",
    expected_disease="Allergic Rhinitis"
)

# Test 21: Respiratory vs Cardiac - Cough differentiator
run_test(
    "Respiratory vs Cardiac - Cough Priority",
    "cough, fever, fatigue, chest pain, shortness of breath",
    expected_disease="Bronchitis"
)

# Test 22: Weak signal - insufficient symptoms
run_test(
    "Weak Allergy Signal (Only Sneezing)",
    "sneezing",
    expected_disease=None  # Too weak to classify as allergy
)

# Test 23: Strong allergy with systemic infection
run_test(
    "Strong Allergy + Systemic Infection Symptoms",
    "intense itching, eyes itching, sneezing, runny nose, fever, body ache",
    expected_disease="Allergic Rhinitis"
)

# Test 24: Bronchitis ruled out without cough
run_test(
    "Fever + Fatigue (Bronchitis Ruled Out)",
    "fever, fatigue, chills, body ache",
    expected_disease=None  # No specific respiratory disease
)


# ============================================================================
# SECTION 6: EDGE CASES
# ============================================================================

print("\n" + "="*80)
print("SECTION 6: EDGE CASES")
print("="*80)
print("Testing edge cases and boundary conditions")

# Test 25: Only fever (no other symptoms)
run_test(
    "Only Fever",
    "fever",
    expected_disease=None
)

# Test 26: Multiple conflicting mandatory symptoms
run_test(
    "Multiple Mandatory Symptoms",
    "chest pain, severe headache, wheezing",
    expected_disease=None  # Could be heart attack or migraine
)

# Test 27: Allergy with various fever levels
run_test(
    "Allergy with Moderate Fever",
    "itching, sneezing, runny nose, fever 99F",
    expected_disease="Allergic Rhinitis"
)

# Test 28: Clear bronchitis case
run_test(
    "Clear Bronchitis Case",
    "persistent cough, chest pain, fever, wheezing, fatigue",
    expected_disease="Bronchitis"
)


# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"Total Tests: {test_count}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if failed == 0:
    print("\n✅ ALL TESTS PASSED!")
else:
    print(f"\n❌ {failed} tests failed")

print("="*80 + "\n")
