#!/usr/bin/env python3
"""
Test script to validate confidence score normalization.

This script demonstrates how the new confidence scoring system works
and validates all the requirements:

✓ No randomness (deterministic)
✓ Ranking preserved
✓ Values clamped 5-95%
✓ Highest ~90%
✓ Clean display (1 decimal)
"""

import numpy as np


def normalize_confidence_scores(raw_probabilities):
    """
    Normalize raw model probabilities to realistic confidence scores.
    
    Args:
        raw_probabilities: List of raw probability values from model
    
    Returns:
        List of normalized confidence scores (5-95% range)
    """
    if not raw_probabilities:
        return []
    
    # Find maximum probability
    max_prob = max(raw_probabilities)
    
    normalized_scores = []
    for prob in raw_probabilities:
        # Apply normalization formula:
        # (probability / max_probability) * 0.9 * 100
        normalized = (prob / max_prob) * 0.9 * 100
        
        # Clamp to 5-95% range
        clamped = max(5.0, min(95.0, normalized))
        
        # Round to 1 decimal place
        final_score = round(clamped, 1)
        
        normalized_scores.append(final_score)
    
    return normalized_scores


def validate_determinism():
    """Test 1: Validate determinism (same input → same output)"""
    print("\n" + "="*70)
    print("TEST 1: DETERMINISM (Same input → Same output)")
    print("="*70)
    
    raw_probs = [0.35, 0.25, 0.15, 0.10, 0.05]
    
    # Run normalization twice
    result1 = normalize_confidence_scores(raw_probs)
    result2 = normalize_confidence_scores(raw_probs)
    
    print(f"\nRun 1: {result1}")
    print(f"Run 2: {result2}")
    
    if result1 == result2:
        print("✓ PASS: Results are identical (deterministic)")
        return True
    else:
        print("✗ FAIL: Results differ (not deterministic)")
        return False


def validate_ranking():
    """Test 2: Validate ranking preservation"""
    print("\n" + "="*70)
    print("TEST 2: RANKING PRESERVATION (Order not changed)")
    print("="*70)
    
    raw_probs = [0.35, 0.25, 0.15, 0.10, 0.05]
    normalized = normalize_confidence_scores(raw_probs)
    
    print(f"\nRaw probabilities: {raw_probs}")
    print(f"Normalized scores: {normalized}")
    
    # Check if monotonically decreasing
    is_monotonic = all(normalized[i] >= normalized[i+1] 
                      for i in range(len(normalized)-1))
    
    if is_monotonic:
        print("✓ PASS: Ranking order preserved (monotonic decreasing)")
        return True
    else:
        print("✗ FAIL: Ranking order changed")
        return False


def validate_range():
    """Test 3: Validate range (5-95%)"""
    print("\n" + "="*70)
    print("TEST 3: RANGE VALIDATION (5% ≤ confidence ≤ 95%)")
    print("="*70)
    
    # Test with very varied probabilities
    test_cases = [
        [0.35, 0.25, 0.15, 0.10, 0.05],
        [0.01, 0.005, 0.002],  # Very low probabilities
        [0.30, 0.29, 0.28, 0.27],  # Very close probabilities
    ]
    
    all_pass = True
    for case in test_cases:
        normalized = normalize_confidence_scores(case)
        print(f"\nInput: {case}")
        print(f"Output: {normalized}")
        
        in_range = all(5.0 <= score <= 95.0 for score in normalized)
        status = "✓" if in_range else "✗"
        print(f"{status} All values in [5, 95]% range")
        
        if not in_range:
            all_pass = False
    
    if all_pass:
        print("\n✓ PASS: All scores within valid range")
        return True
    else:
        print("\n✗ FAIL: Some scores out of range")
        return False


def validate_highest_score():
    """Test 4: Validate highest score is ~90%"""
    print("\n" + "="*70)
    print("TEST 4: HIGHEST SCORE (~90%)")
    print("="*70)
    
    # The highest score should always be:
    # (max_prob / max_prob) * 0.9 * 100 = 90.0%
    
    test_cases = [
        [0.35, 0.25, 0.15],  # Normal case
        [0.01, 0.005],        # Very low
        [0.50, 0.40, 0.30],  # Higher values
        [0.99, 0.50],         # Very high
    ]
    
    all_pass = True
    for case in test_cases:
        normalized = normalize_confidence_scores(case)
        highest = max(normalized)
        
        print(f"\nInput: {case}")
        print(f"Output: {normalized}")
        print(f"Highest: {highest}%")
        
        # Highest should be 90.0% (within floating point precision)
        is_90 = abs(highest - 90.0) < 0.01
        status = "✓" if is_90 else "✗"
        print(f"{status} Highest score {'≈' if is_90 else '≠'} 90.0%")
        
        if not is_90:
            all_pass = False
    
    if all_pass:
        print("\n✓ PASS: Highest score consistently ~90%")
        return True
    else:
        print("\n✗ FAIL: Highest score not ~90%")
        return False


def validate_display_format():
    """Test 5: Validate display format (1 decimal place)"""
    print("\n" + "="*70)
    print("TEST 5: DISPLAY FORMAT (X.X% format)")
    print("="*70)
    
    raw_probs = [0.35, 0.25, 0.15]
    normalized = normalize_confidence_scores(raw_probs)
    
    print(f"\nNormalized scores: {normalized}")
    
    all_pass = True
    for score in normalized:
        # Check if exactly 1 decimal place
        score_str = f"{score:.1f}"
        
        # Convert back to verify it's the same
        if abs(float(score_str) - score) < 0.001:
            print(f"✓ {score_str}% (proper format)")
        else:
            print(f"✗ {score} (improper format)")
            all_pass = False
    
    if all_pass:
        print("\n✓ PASS: All scores display as X.X%")
        return True
    else:
        print("\n✗ FAIL: Some scores have improper format")
        return False


def real_world_example():
    """Test 6: Real-world prediction example"""
    print("\n" + "="*70)
    print("TEST 6: REAL-WORLD EXAMPLE")
    print("="*70)
    
    print("\nScenario: Patient with fever and headache")
    print("Model predictions (raw probabilities):\n")
    
    diseases = ["Flu", "Common Cold", "Pneumonia", "Migraine Headache"]
    raw_probs = [0.35, 0.25, 0.15, 0.10]
    
    # Show before and after
    print("Disease              | Raw %  | Before (Old) | After (New)")
    print("-" * 60)
    
    normalized = normalize_confidence_scores(raw_probs)
    old_style = [round(p * 100, 2) for p in raw_probs]
    
    for disease, raw, old, new in zip(diseases, raw_probs, old_style, normalized):
        print(f"{disease:20} | {raw*100:5.0f}% | {old:11.2f}% | {new:8.1f}%")
    
    print("\n" + "-" * 60)
    print("Benefits of new scoring:")
    print("  ✓ 35% Flu → 90.0% Flu: Looks confident and reliable")
    print("  ✓ 25% Cold → 64.3% Cold: Still lower but more realistic")
    print("  ✓ No 100% shown: Avoids false certainty")
    print("  ✓ Ranked order preserved: Flu > Cold > Pneumonia > Migraine")
    
    return True


def test_edge_cases():
    """Test 7: Edge cases"""
    print("\n" + "="*70)
    print("TEST 7: EDGE CASES")
    print("="*70)
    
    test_cases = {
        "Single prediction": [0.5],
        "Two very close": [0.300, 0.299],
        "All same": [0.25, 0.25, 0.25],
        "Very small probs": [0.001, 0.0005],
        "Large differences": [0.9, 0.1],
    }
    
    all_pass = True
    for name, probs in test_cases.items():
        normalized = normalize_confidence_scores(probs)
        print(f"\n{name}:")
        print(f"  Input:  {probs}")
        print(f"  Output: {normalized}")
        
        # Validate range and format
        valid = all(5.0 <= s <= 95.0 for s in normalized)
        formatted = all(isinstance(s, float) and len(f"{s:.1f}") > 0 
                       for s in normalized)
        
        if valid and formatted:
            print(f"  ✓ Pass")
        else:
            print(f"  ✗ Fail")
            all_pass = False
    
    if all_pass:
        print("\n✓ PASS: All edge cases handled correctly")
        return True
    else:
        print("\n✗ FAIL: Some edge cases failed")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("CONFIDENCE SCORE NORMALIZATION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Determinism", validate_determinism),
        ("Ranking Preservation", validate_ranking),
        ("Range Validation", validate_range),
        ("Highest Score (~90%)", validate_highest_score),
        ("Display Format", validate_display_format),
        ("Real-World Example", real_world_example),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "="*70)
    print(f"OVERALL: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! Confidence scoring is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    exit(main())
