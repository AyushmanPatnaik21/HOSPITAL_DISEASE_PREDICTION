#!/usr/bin/env python3
"""
Cleanup script - Remove unwanted test and documentation files
"""
import os
import sys

# Change to project directory
os.chdir(r'C:\Users\asuto\Desktop\Hospital')

# Files to remove
files_to_remove = [
    # Test files
    'test_advanced_logic.py',
    'test_allergy_cold_disambiguation.py',
    'test_confidence_scoring.py',
    'test_diabetes_override.py',
    'test_flask_integration.py',
    'test_hybrid_ai.py',
    'test_strict_category_filtering.py',
    'test_symptom_conflict_resolution.py',
    'test_symptom_extraction_final.py',
    'test_symptom_extraction_fix.py',
    # Documentation files
    'ALLERGY_COLD_DISAMBIGUATION.md',
    'DEVELOPER_GUIDE.md',
    'FINAL_SUMMARY.md',
    'HOSPITAL_AI_PREDICTION_SUMMARY.md',
    'QUICK_REFERENCE.md',
    'STRICT_CATEGORY_FILTERING.md',
    'STRICT_FILTERING_IMPLEMENTATION.md',
    'SYMPTOM_EXTRACTION_IMPROVEMENTS.md',
    'UPGRADE_SUMMARY.md',
    'SYMPTOM_CONFLICT_RESOLUTION.md',
    # Text files
    'ALLERGY_COLD_IMPLEMENTATION.txt',
    'IMPLEMENTATION_COMPLETE.txt',
    # Demo and temporary files
    'diabetes_demo.py',
    'tmp_patch_ai_predictor.py',
]

removed = []
errors = []

for filename in files_to_remove:
    filepath = os.path.join(os.getcwd(), filename)
    try:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)
            removed.append(filename)
            print(f"✅ Removed: {filename}")
        else:
            print(f"⏭️  Not found: {filename}")
    except Exception as e:
        errors.append((filename, str(e)))
        print(f"❌ Error removing {filename}: {e}")

print(f"\n{'='*60}")
print(f"CLEANUP SUMMARY")
print(f"{'='*60}")
print(f"Total Removed: {len(removed)} files")
print(f"Errors: {len(errors)}")

if removed:
    print(f"\n✅ Successfully removed:")
    for f in removed:
        print(f"   - {f}")

if errors:
    print(f"\n❌ Errors:")
    for f, e in errors:
        print(f"   - {f}: {e}")

print(f"\n📁 Remaining essential files in project:")
remaining = [f for f in os.listdir('.') if os.path.isfile(f)]
remaining.sort()
for f in remaining:
    if not f.startswith('.'):
        print(f"   ✓ {f}")

print(f"\n✅ Cleanup complete!")
