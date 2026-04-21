#!/usr/bin/env python3
import os
import sys

# Absolute paths to files to delete
files_to_delete = [
    r'C:\Users\asuto\Desktop\Hospital\ALLERGY_COLD_DISAMBIGUATION.md',
    r'C:\Users\asuto\Desktop\Hospital\CLEANUP_GUIDE.md',
    r'C:\Users\asuto\Desktop\Hospital\DEVELOPER_GUIDE.md',
    r'C:\Users\asuto\Desktop\Hospital\FINAL_SUMMARY.md',
    r'C:\Users\asuto\Desktop\Hospital\HOSPITAL_AI_PREDICTION_SUMMARY.md',
    r'C:\Users\asuto\Desktop\Hospital\QUICK_REFERENCE.md',
    r'C:\Users\asuto\Desktop\Hospital\STRICT_CATEGORY_FILTERING.md',
    r'C:\Users\asuto\Desktop\Hospital\STRICT_FILTERING_IMPLEMENTATION.md',
    r'C:\Users\asuto\Desktop\Hospital\SYMPTOM_EXTRACTION_IMPROVEMENTS.md',
    r'C:\Users\asuto\Desktop\Hospital\UPGRADE_SUMMARY.md',
    r'C:\Users\asuto\Desktop\Hospital\SYMPTOM_CONFLICT_RESOLUTION.md'
]

print("Starting deletion...")
deleted = 0

for filepath in files_to_delete:
    filename = os.path.basename(filepath)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            deleted += 1
            print(f'✅ Deleted: {filename}')
        else:
            print(f'⏭️  Not found: {filename}')
    except PermissionError as e:
        print(f'❌ Permission denied: {filename}')
    except Exception as e:
        print(f'❌ Error deleting {filename}: {e}')

print(f'\nSummary: Deleted {deleted}/{len(files_to_delete)} files')
print('Keeping: summary.md, README.md')
