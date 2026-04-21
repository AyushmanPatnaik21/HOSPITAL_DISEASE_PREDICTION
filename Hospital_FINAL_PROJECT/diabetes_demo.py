#!/usr/bin/env python3
"""
Quick demo of the diabetes rule-based override system.
"""

from ai_engine.ai_predictor import AIPredictor

def main():
    predictor = AIPredictor()

    # Test diabetes detection
    test_cases = [
        'frequent urination, increased thirst',
        'I have been urinating frequently and feeling very thirsty',
        'polyuria and polydipsia',
        'pee a lot and always thirsty',
        'fever, cough',  # Should NOT trigger diabetes
    ]

    print('🩺 DIABETES DETECTION DEMO')
    print('=' * 50)

    for i, case in enumerate(test_cases, 1):
        print(f'{i}. Input: "{case}"')
        result = predictor.predict(case)
        if result['predictions']:
            disease = result['predictions'][0]['disease']
            confidence = result['predictions'][0]['confidence']
            print(f'   → {disease} ({confidence:.1f}%)')
        print()

if __name__ == '__main__':
    main()