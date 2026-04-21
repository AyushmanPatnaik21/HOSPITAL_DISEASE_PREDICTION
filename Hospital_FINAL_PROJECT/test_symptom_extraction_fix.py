#!/usr/bin/env python3
"""
Test suite for improved symptom extraction with synonym mapping.

Tests the fixed extract_symptoms method with real-world medical variations
and ensures that natural language phrases are correctly mapped to dataset symptoms.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_engine.ai_predictor import AIPredictor


def test_symptom_extraction():
    """Test all symptom extraction cases."""
    
    print("=" * 80)
    print("SYMPTOM EXTRACTION TESTS - Improved Multi-Tier Matching")
    print("=" * 80)
    print()
    
    predictor = AIPredictor()
    
    # Test cases with expected results
    test_cases = [
        # ===== ORIGINAL FAILING CASE =====
        {
            "name": "Diabetes symptoms (original failing case)",
            "input": "frequent urination, increased thirst, weight loss",
            "should_contain": ["weakness", "fatigue", "weight_loss"],
            "description": "Should detect diabetes indicators via synonym mapping"
        },
        
        # ===== MULTI-WORD PHRASE MATCHING =====
        {
            "name": "Common cold symptoms",
            "input": "sore throat, runny nose, cough",
            "should_contain": ["sore_throat", "runny_nose", "cough"],
            "description": "Multi-word symptom phrases should be detected"
        },
        
        # ===== SYNONYM VARIATIONS =====
        {
            "name": "Fever variations",
            "input": "high fever, body temperature elevated",
            "should_contain": ["fever"],
            "description": "Various fever descriptions should map to 'fever'"
        },
        
        {
            "name": "Breathing issues",
            "input": "shortness of breath, difficulty breathing",
            "should_contain": ["shortness_of_breath", "difficulty_breathing"],
            "description": "Breathing variations should be detected"
        },
        
        # ===== CHEST PAIN (CRITICAL) =====
        {
            "name": "Heart attack warning signs",
            "input": "chest pain, arm pain, shortness of breath",
            "should_contain": ["chest_pain", "arm_pain", "shortness_of_breath"],
            "description": "Critical symptoms should be accurately detected"
        },
        
        # ===== STOMACH/GI ISSUES =====
        {
            "name": "Stomach problems",
            "input": "stomach pain, nausea, vomiting",
            "should_contain": ["nausea", "vomiting"],
            "description": "GI symptoms should be detected despite alternate phrasing"
        },
        
        # ===== JOINT/MUSCLE ISSUES =====
        {
            "name": "Joint pain and stiffness",
            "input": "joint pain, morning stiffness, muscle weakness",
            "should_contain": ["joint_pain", "joint_stiffness", "muscle_weakness"],
            "description": "Rheumatoid arthritis symptoms detected"
        },
        
        # ===== SKIN ISSUES =====
        {
            "name": "Rash and itching",
            "input": "skin rash, itching, scabs",
            "should_contain": ["rash", "itching", "scabs"],
            "description": "Skin conditions properly detected"
        },
        
        # ===== NEUROLOGICAL =====
        {
            "name": "Neurological symptoms",
            "input": "severe headache, dizziness, confusion, memory loss",
            "should_contain": ["severe_headache", "dizziness", "confusion", "memory_problems"],
            "description": "Should detect neuro symptoms"
        },
        
        # ===== EDGE CASES =====
        {
            "name": "Complex natural language",
            "input": "I have been experiencing a high fever and severe headache for 3 days with body aches",
            "should_contain": ["fever", "severe_headache", "body_ache"],
            "description": "Natural full sentences should be parsed correctly"
        },
        
        {
            "name": "Comma-separated symptoms",
            "input": "fever, cough, runny nose",
            "should_contain": ["fever", "cough", "runny_nose"],
            "description": "Comma-separated list format should work"
        },
    ]
    
    # Track results
    passed = 0
    failed = 0
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTEST {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        print(f"Description: {test_case['description']}")
        print(f"Expected to contain: {test_case['should_contain']}")
        print()
        
        # Extract symptoms
        extracted = predictor.extract_symptoms(test_case['input'])
        
        # Check results
        success = True
        missing = []
        for expected_symptom in test_case['should_contain']:
            if expected_symptom not in extracted:
                success = False
                missing.append(expected_symptom)
        
        if success:
            print(f"✅ PASSED - All expected symptoms found")
            passed += 1
            results.append((test_case['name'], True))
        else:
            print(f"❌ FAILED - Missing symptoms: {missing}")
            failed += 1
            results.append((test_case['name'], False))
        
        print("-" * 80)
    
    # Print summary
    print()
    print("=" * 80)
    print(f"SUMMARY: {passed}/{len(test_cases)} tests passed")
    print("=" * 80)
    print()
    
    if failed > 0:
        print("Failed tests:")
        for name, result in results:
            if not result:
                print(f"  ❌ {name}")
    
    print()
    print("Test Details:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    return failed == 0


def test_diabetes_detection():
    """Specifically test diabetes prediction with improved symptom extraction."""
    
    print()
    print("=" * 80)
    print("DIABETES PREDICTION TEST - Real-world scenario")
    print("=" * 80)
    print()
    
    predictor = AIPredictor()
    
    # Diabetes symptoms input
    user_input = "frequent urination, increased thirst, weight loss, fatigue"
    print(f"User input: '{user_input}'")
    print()
    
    # Extract symptoms
    print("STEP 1: Extract symptoms...")
    print()
    extracted_symptoms = predictor.extract_symptoms(user_input)
    print(f"Extracted: {extracted_symptoms}")
    print()
    
    # Make prediction using the original input string
    print("STEP 2: Make prediction...")
    print()
    prediction_result = predictor.predict(user_input)
    
    # Check validation
    if not prediction_result['input_validation']['valid']:
        print(f"⚠️  Validation failed: {prediction_result['input_validation']['message']}")
        print()
        return False
    
    # Get top prediction
    if prediction_result['predictions']:
        top_pred = prediction_result['predictions'][0]
        print(f"Top prediction: {top_pred['disease']}")
        print(f"Confidence: {top_pred['confidence']}%")
        print()
        
        # Check if diabetes is in top predictions
        if 'diabetes' in top_pred['disease'].lower():
            print("✅ SUCCESS - Diabetes correctly predicted!")
            print()
            print(f"Full predictions:")
            for i, pred in enumerate(prediction_result['predictions'], 1):
                print(f"  {i}. {pred['disease']}: {pred['confidence']}%")
            return True
        else:
            print(f"⚠️  Note: Top prediction is {top_pred['disease']}")
            print(f"Check if Diabetes is in predictions:")
            diabetes_found = False
            for pred in prediction_result['predictions']:
                print(f"  - {pred['disease']}: {pred['confidence']}%")
                if 'diabetes' in pred['disease'].lower():
                    diabetes_found = True
            if diabetes_found:
                print(f"  ✅ Diabetes found in top predictions")
                return True
            else:
                print(f"  ℹ️ Diabetes not in top predictions")
                return False
    else:
        print(f"❌ No predictions returned")
        print(f"Validation: {prediction_result['input_validation']}")
        return False


def show_available_symptoms():
    """Show available symptoms in the dataset."""
    
    print()
    print("=" * 80)
    print("AVAILABLE SYMPTOMS IN DATASET")
    print("=" * 80)
    print()
    
    predictor = AIPredictor()
    symptoms = sorted(predictor.symptoms_list)
    
    print(f"Total symptoms: {len(symptoms)}")
    print()
    print("Symptoms (sample - first 30):")
    for symptom in symptoms[:30]:
        print(f"  • {symptom}")
    
    print()
    print(f"... and {len(symptoms) - 30} more")
    print()


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " IMPROVED SYMPTOM EXTRACTION - COMPREHENSIVE TEST SUITE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Show available symptoms for reference
    show_available_symptoms()
    
    # Run main tests
    print()
    all_passed = test_symptom_extraction()
    
    # Run diabetes-specific test
    diabetes_ok = test_diabetes_detection()
    
    # Final summary
    print()
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print()
    print(f"Symptom extraction tests: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    print(f"Diabetes detection: {'✅ SUCCESS' if diabetes_ok else '⚠️ CHECK NEEDED'}")
    print()
    
    if all_passed and diabetes_ok:
        print("🎉 FIX IS WORKING - All tests passed!")
    
    print()
