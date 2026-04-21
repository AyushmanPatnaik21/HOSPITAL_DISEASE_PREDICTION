from pathlib import Path
import re

path = Path('ai_engine/ai_predictor.py')
text = path.read_text(encoding='utf-8')
pattern = re.compile(r"(\s*# Normalize input.*?return result\n)(\s*)def validate_symptoms\(", re.S)
replacement = '''        if not natural_language_input or not isinstance(natural_language_input, str):
            return []

        original_input = natural_language_input
        text_lower = natural_language_input.lower().strip()
        text_lower = re.sub(r'[,;:\\-—–]', ' ', text_lower)
        text_lower = re.sub(r'\\s+', ' ', text_lower).strip()

        matched_symptoms = set()
        skip_words = {
            'pain', 'ache', 'aching', 'soreness', 'issue', 'problem',
            'symptom', 'symptoms', 'sick', 'ill', 'bad', 'good', 'ok', 'okay',
            'help', 'medical', 'condition', 'disease', 'health', 'body', 'having',
            'feel', 'feeling', 'have', 'has', 'had', 'been', 'very'
        }

        sorted_variations = sorted(self.SYMPTOM_VARIATIONS.items(), key=lambda item: len(item[0].split()), reverse=True)
        tokens = text_lower.split()
        idx = 0

        while idx < len(tokens):
            matched_phrase = False
            for phrase, symptom in sorted_variations:
                phrase_tokens = phrase.split()
                if tokens[idx:idx + len(phrase_tokens)] == phrase_tokens:
                    matched_symptoms.add(symptom)
                    print(f"  EXPLICIT MATCH: '{phrase}' → '{symptom}'")
                    idx += len(phrase_tokens)
                    matched_phrase = True
                    break
            if matched_phrase:
                continue

            token = tokens[idx]
            if token in skip_words:
                idx += 1
                continue

            normalized = self._normalize_symptom(token)
            if normalized:
                matched_symptoms.add(normalized)
                print(f"  SINGLE WORD MATCH: '{token}' → '{normalized}'")
                idx += 1
                continue

            if token in self.symptoms_list:
                matched_symptoms.add(token)
                print(f"  DIRECT LIST MATCH: '{token}'")
                idx += 1
                continue

            idx += 1

        result = sorted(matched_symptoms)
        print(f"DEBUG: extract_symptoms('{original_input}')")
        print(f"  RESULT: {result if result else 'NO SYMPTOMS MATCHED'}")
        print()
        return result

    def _extract_rule_symptoms(self, natural_language_input: str) -> List[str]:
        """
        Extract rule-only symptom aliases from user input.
        These are used for hybrid override logic and are not necessarily in the dataset symptom list.
        """
        if not natural_language_input or not isinstance(natural_language_input, str):
            return []

        text_lower = natural_language_input.lower().strip()
        text_lower = re.sub(r'[,;:\\-—–]', ' ', text_lower)
        text_lower = re.sub(r'\\s+', ' ', text_lower).strip()
        tokens = text_lower.split()

        rule_symptoms = set()
        sorted_aliases = sorted(self.RULE_SYMPTOM_ALIASES.items(), key=lambda item: len(item[0].split()), reverse=True)
        idx = 0

        while idx < len(tokens):
            matched_alias = False
            for phrase, alias in sorted_aliases:
                phrase_tokens = phrase.split()
                if tokens[idx:idx + len(phrase_tokens)] == phrase_tokens:
                    rule_symptoms.add(alias)
                    print(f"  RULE SYMPTOM MATCH: '{phrase}' → '{alias}'")
                    idx += len(phrase_tokens)
                    matched_alias = True
                    break
            if not matched_alias:
                idx += 1

        return sorted(rule_symptoms)

    def validate_symptoms(self, symptoms: List[str]) -> Tuple[bool, str]:
'''
match = pattern.search(text)
if not match:
    raise SystemExit('Could not find extract_symptoms block for replacement')
text = text[:match.start(1)] + replacement + text[match.end(1):]
path.write_text(text, encoding='utf-8')
print('Updated extract_symptoms and added _extract_rule_symptoms')
