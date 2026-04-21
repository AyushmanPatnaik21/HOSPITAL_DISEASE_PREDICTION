#!/usr/bin/env python3
"""
Test suite for rule-based Diabetes override and corrected symptom mapping.

Tests the fix for incorrect symptom mappings and rule-based override for
diseases not present in the trained ML model.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_engine.ai_predictor import AIPredictor


def test_diabetes_rule_override():
    """Test that Diabetes is correctly detected via rule-based override."""
    
    print("\n" + "=" * 80)
    print("DIABETES RULE-BASED OVERRIDE TEST")
    print("=" * 80)
    print()
    
    predictor = AIPredictor()
    
    # Test cases for Diabetes override
    diabetes_test_cases = [
        {
            "name": "Classic Diabetes symptoms",
            "input": "frequent urination, increased thirst, weight loss",
            "expected_disease": "Diabetes",
            "expected_confidence": 90.0,
            "expected_symptoms": ["frequent urination", "increased thirst", "weight loss"]
        },
        {
            "name": "Diabetes with natural language",
            "input": "I have been urinating frequently and feeling very thirsty, also lost weight",
            "expected_disease": "Diabetes",
            "expected_confidence": 90.0,
            "expected_symptoms": ["frequent urination", "increased thirst", "weight loss"]
        },
        {
            "name": "Partial Diabetes symptoms (should still trigger)",
            "input": "frequent urination and increased thirst",
            "expected_disease": "Diabetes",
            "expected_confidence": 90.0,
            "expected_symptoms": ["frequent urination", "increased thirst"]
        },
        {
            "name": "Only frequent urination (should NOT trigger Diabetes)",
            "input": "frequent urination",
            "expected_disease": "NOT Diabetes",
            "expected_confidence": "NOT 90.0"
        },
        {
            "name": "Only increased thirst (should NOT trigger Diabetes)",
            "input": "increased thirst",
            "expected_disease": "NOT Diabetes",
            "expected_confidence": "NOT 90.0"
        }
    ]
    
    print("Testing Diabetes rule-based override:")
    print()
    
    passed = 0
    total = len(diabetes_test_cases)
    
    for i, test_case in enumerate(diabetes_test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        print()
        
        # Make prediction
        result = predictor.predict(test_case['input'])
        
        if result['predictions']:
            top_pred = result['predictions'][0]
            disease = top_pred['disease']
            confidence = top_pred['confidence']
            symptoms = result['symptoms']
            
            print(f"Predicted: {disease} ({confidence}%)")
            print(f"Symptoms: {symptoms}")
            print()
            
            # Check if this should be Diabetes
            if test_case['expected_disease'] == "Diabetes":
                if disease == "Diabetes" and confidence == 90.0:
                    print("✅ PASSED - Diabetes correctly detected via rule override")
                    passed += 1
                else:
                    print(f"❌ FAILED - Expected Diabetes (90.0%), got {disease} ({confidence}%)")
            else:
                if disease != "Diabetes" or confidence != 90.0:
                    print("✅ PASSED - Diabetes override correctly NOT triggered")
                    passed += 1
                else:
                    print(f"❌ FAILED - Diabetes override triggered when it shouldn't: {disease} ({confidence}%)")
        else:
            print("❌ FAILED - No predictions returned")
        
        print("-" * 80)
    
    print(f"\nDiabetes Override Tests: {passed}/{total} PASSED")
    return passed == total


def test_symptom_extraction_no_wrong_mappings():
    """Test that incorrect symptom mappings have been removed."""
    
    print("\n" + "=" * 80)
    print("SYMPTOM EXTRACTION - NO WRONG MAPPINGS TEST")
    print("=" * 80)
    print()
    
    predictor = AIPredictor()
    
    # Test that these phrases are NOT mapped to wrong symptoms
    wrong_mapping_tests = [
        {
            "input": "frequent urination",
            "should_not_contain": ["weakness"],
            "description": "frequent urination should NOT map to weakness"
        },
        {
            "input": "increased thirst",
            "should_not_contain": ["fatigue"],
            "description": "increased thirst should NOT map to fatigue"
        },
        {
            "input": "excessive thirst",
            "should_not_contain": ["fatigue"],
            "description": "excessive thirst should NOT map to fatigue"
        },
        {
            "input": "polyuria",
            "should_not_contain": ["weakness"],
            "description": "polyuria should NOT map to weakness"
        }
    ]
    
    print("Testing that incorrect mappings have been removed:")
    print()
    
    passed = 0
    total = len(wrong_mapping_tests)
    
    for i, test_case in enumerate(wrong_mapping_tests, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Input: '{test_case['input']}'")
        
        # Extract symptoms
        symptoms = predictor.extract_symptoms(test_case['input'])
        print(f"Extracted: {symptoms}")
        
        # Check that wrong mappings are NOT present
        has_wrong_mapping = any(wrong in symptoms for wrong in test_case['should_not_contain'])
        
        if not has_wrong_mapping:
            print("✅ PASSED - No incorrect mapping found")
            passed += 1
        else:
            print(f"❌ FAILED - Found incorrect mapping: {test_case['should_not_contain']}")
        
        print()
    
    print(f"Wrong Mapping Removal Tests: {passed}/{total} PASSED")
    return passed == total


def test_normal_disease_predictions_still_work():
    """Test that normal disease predictions still work correctly."""
    
    print("\n" + "=" * 80)
    print("NORMAL DISEASE PREDICTIONS - STILL WORKING TEST")
    print("=" * 80)
    print()
    
    predictor = AIPredictor()
    
    # Test cases for diseases that ARE in the model
    normal_tests = [
        {
            "name": "Flu symptoms",
            "input": "fever, cough, body aches",
            "expected_in_top": ["Flu", "Pneumonia", "Bronchitis"]
        },
        {
            "name": "Heart attack symptoms",
            "input": "chest pain, shortness of breath",
            "expected_in_top": ["Heart Attack"]
        },
        {
            "name": "Migraine symptoms",
            "input": "severe headache, nausea",
            "expected_in_top": ["Migraine"]
        }
    ]
    
    print("Testing that normal disease predictions still work:")
    print()
    
    passed = 0
    total = len(normal_tests)
    
    for i, test_case in enumerate(normal_tests, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        
        # Make prediction
        result = predictor.predict(test_case['input'])
        
        if result['predictions']:
            top_diseases = [pred['disease'] for pred in result['predictions'][:3]]
            print(f"Top predictions: {top_diseases}")
            
            # Check if expected disease is in top 3
            found_expected = any(exp in top_diseases for exp in test_case['expected_in_top'])
            
            if found_expected:
                print("✅ PASSED - Expected disease in top predictions")
                passed += 1
            else:
                print(f"❌ FAILED - Expected {test_case['expected_in_top']} not in {top_diseases}")
        else:
            print("❌ FAILED - No predictions returned")
        
        print()
    
    print(f"Normal Predictions Tests: {passed}/{total} PASSED")
    return passed == total


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " RULE-BASED DIABETES OVERRIDE & SYMPTOM MAPPING FIXES".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Run all tests
    diabetes_ok = test_diabetes_rule_override()
    mappings_ok = test_symptom_extraction_no_wrong_mappings()
    normal_ok = test_normal_disease_predictions_still_work()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    print()
    print(f"Diabetes Rule Override: {'✅ PASSED' if diabetes_ok else '❌ FAILED'}")
    print(f"Wrong Mappings Removed: {'✅ PASSED' if mappings_ok else '❌ FAILED'}")
    print(f"Normal Predictions: {'✅ PASSED' if normal_ok else '❌ FAILED'}")
    print()
    
    if diabetes_ok and mappings_ok and normal_ok:
        print("🎉 ALL TESTS PASSED - Rule-based Diabetes override working correctly!")
        print("   - Incorrect symptom mappings removed")
        print("   - Diabetes detected via rule-based override")
        print("   - Normal disease predictions unchanged")
    else:
        print("⚠️  Some tests failed - check output above")
    
    print()
