import os
import sys

os.chdir(r'C:\Users\asuto\Desktop\Hospital')

files_to_delete = [
    'ALLERGY_COLD_DISAMBIGUATION.md',
    'CLEANUP_GUIDE.md',
    'DEVELOPER_GUIDE.md',
    'FINAL_SUMMARY.md',
    'HOSPITAL_AI_PREDICTION_SUMMARY.md',
    'QUICK_REFERENCE.md',
    'STRICT_CATEGORY_FILTERING.md',
    'STRICT_FILTERING_IMPLEMENTATION.md',
    'SYMPTOM_EXTRACTION_IMPROVEMENTS.md',
    'UPGRADE_SUMMARY.md',
    'SYMPTOM_CONFLICT_RESOLUTION.md'
]

deleted = 0
for filename in files_to_delete:
    filepath = os.path.abspath(filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            deleted += 1
            print(f'✅ {filename}')
        except PermissionError:
            print(f'❌ Permission denied: {filename}')
        except Exception as e:
            print(f'❌ {filename}: {type(e).__name__}')

print(f'\nDeleted: {deleted}/{len(files_to_delete)} files')
print('Keeping: summary.md, README.md')
