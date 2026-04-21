"""
AI Predictor Module - Disease Prediction Engine
Provides intelligent symptom analysis and disease prediction using ML models.

CRITICAL: This module fixes prediction logic WITHOUT changing:
- Dataset
- Model (model.pkl)
- Feature mappings (symptoms.pkl)

Features:
- Correct symptom extraction from natural language
- Proper feature vector creation (aligned with model expectations)
- Accurate predictions using model.predict_proba()
- Confidence-based filtering (0.5 threshold)
- Medical-logical explanations
- Severity detection based on critical symptoms
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple, Set
import re
from pathlib import Path
from difflib import SequenceMatcher


class AIPredictor:
    """
    Advanced disease prediction engine using trained ML models.
    
    Attributes:
        model: Trained disease prediction model
        symptom_encoder: MultiLabelBinarizer for symptoms
        disease_encoder: LabelEncoder for disease names
        symptoms_list: Complete list of valid symptoms
        critical_symptoms: High-severity symptoms
        symptom_variations: Mapping of common variations to canonical symptoms
    """
    
    # Critical symptoms that indicate high severity
    CRITICAL_SYMPTOMS = {
        'chest_pain', 'chest pain',
        'shortness_of_breath', 'shortness of breath',
        'difficulty_breathing', 'difficulty breathing',
        'severe_headache', 'severe headache',
        'loss_of_consciousness', 'loss of consciousness',
        'severe_vomiting', 'severe vomiting',
        'difficulty_swallowing', 'difficulty swallowing',
        'palpitations', 'tremor'
    }
    
    # Symptom variations/synonyms normalization
    # Maps real-world phrases and common variations to canonical dataset symptoms
    SYMPTOM_VARIATIONS = {
        # === FEVER VARIATIONS ===
        'high fever': 'fever',
        'low fever': 'fever',
        'mild fever': 'mild_fever',
        'temperature': 'fever',
        'burning': 'fever',
        'body temperature': 'fever',
        'elevated temperature': 'fever',
        'body temp': 'fever',
        'running a fever': 'fever',
        
        # === GENERAL ACHES/PAIN ===
        'ache': 'body_ache',  # Convert to body_ache instead of pain
        'aching': 'body_ache',
        'aches': 'body_ache',
        'body aches': 'body_ache',
        'sore': 'sore_throat',  # Likely means sore throat
        'soreness': 'body_ache',
        'body pain': 'body_ache',
        'muscle ache': 'muscle_pain',
        'joint ache': 'joint_pain',
        
        # === COUGH VARIATIONS ===
        'coughing': 'cough',
        'dry cough': 'cough',
        'wet cough': 'cough',
        'persistent cough': 'persistent_cough',
        'chronic cough': 'persistent_cough',
        'hacking cough': 'cough',
        'coughing a lot': 'persistent_cough',
        
        # === HEADACHE VARIATIONS ===
        'head pain': 'headache',
        'migraine': 'severe_headache',
        'head ache': 'headache',
        'severe headache': 'severe_headache',
        'bad headache': 'severe_headache',
        'splitting headache': 'severe_headache',
        'terrible headache': 'severe_headache',
        
        # === BREATHING ISSUES ===
        'breathlessness': 'shortness_of_breath',
        'unable to breathe': 'shortness_of_breath',
        'breath shortness': 'shortness_of_breath',
        'cannot breathe': 'difficulty_breathing',
        'hard to breathe': 'difficulty_breathing',
        'shortness of breath': 'shortness_of_breath',
        'chest tightness': 'shortness_of_breath',
        'having trouble breathing': 'difficulty_breathing',
        'breathing difficulty': 'difficulty_breathing',
        'difficult breathing': 'difficulty_breathing',
        'out of breath': 'shortness_of_breath',
        'difficulty breathing': 'difficulty_breathing',
        'trouble breathing': 'difficulty_breathing',
        'breathing problems': 'difficulty_breathing',
        
        # === CHEST PAIN (CRITICAL) ===
        'chest pain': 'chest_pain',
        'chest pains': 'chest_pain',
        'chest ache': 'chest_pain',
        'chest discomfort': 'chest_pain',
        'heart pain': 'chest_pain',
        'pain in chest': 'chest_pain',
        'chest tightness': 'chest_pain',
        'tightness in chest': 'chest_pain',
        
        # === STOMACH/GI ISSUES ===
        'stomach pain': 'abdominal_pain',
        'stomach ache': 'stomach_cramps',
        'belly pain': 'abdominal_pain',
        'abdominal pain': 'abdominal_pain',
        'upset stomach': 'nausea',
        'stomach upset': 'nausea',
        'feeling sick': 'nausea',
        'feeling nauseous': 'nausea',
        'stomachache': 'stomach_cramps',
        'stomach cramps': 'stomach_cramps',
        'intestinal pain': 'abdominal_pain',
        'belly ache': 'abdominal_pain',
        'gut pain': 'abdominal_pain',
        
        # === VOMITING/NAUSEA ===
        'throwing up': 'vomiting',
        'throwing up food': 'vomiting',
        'retching': 'vomiting',
        'gagging': 'vomiting',
        'want to vomit': 'nausea',
        'feel like vomiting': 'nausea',
        'nausea': 'nausea',
        'sick feeling': 'nausea',
        'vomiting': 'vomiting',
        
        # === THROAT ISSUES ===
        'sore throat': 'sore_throat',
        'throat pain': 'sore_throat',
        'throat ache': 'sore_throat',
        'throat infection': 'sore_throat',
        'swollen tonsils': 'swollen_tonsils',
        'tonsil pain': 'swollen_tonsils',
        'scratchy throat': 'sore_throat',
        'throat soreness': 'sore_throat',
        
        # === NOSE/RUNNY NOSE ===
        'runny nose': 'runny_nose',
        'nasal congestion': 'runny_nose',
        'congestion': 'runny_nose',
        'sniffles': 'runny_nose',
        'stuffy nose': 'runny_nose',
        'nose congestion': 'runny_nose',
        'runny nasal': 'runny_nose',
        
        # === RASH/SKIN ===
        'skin irritation': 'skin_rash',
        'rash': 'rash',
        'skin rash': 'rash',
        'body rash': 'rash',
        'red rash': 'rash',
        'skin eruption': 'rash',
        'itchy rash': 'rash',
        'itchy': 'itching',
        'itching': 'itching',
        'itches': 'itching',
        'itchy skin': 'itching',
        'scabs': 'scabs',
        'blisters': 'blistering',
        'blister': 'blistering',
        'hair loss': 'hair_loss',
        'losing hair': 'hair_loss',
        
        # === FATIGUE/WEAKNESS ===
        'weak': 'weakness',
        'weakness': 'weakness',
        'tired': 'fatigue',
        'tired feeling': 'fatigue',
        'exhausted': 'fatigue',
        'sleepy': 'fatigue',
        'sleepiness': 'fatigue',
        'no energy': 'fatigue',
        'lack of energy': 'fatigue',
        'feeling tired': 'fatigue',
        'very tired': 'fatigue',
        'extreme fatigue': 'fatigue',
        'worn out': 'fatigue',
        
        # === SWEATING ===
        'sweating': 'sweating',
        'perspiration': 'sweating',
        'perspiring': 'sweating',
        'sweaty': 'sweating',
        'night sweat': 'night_sweats',
        'night sweats': 'night_sweats',
        'sweating at night': 'night_sweats',
        'cold sweat': 'sweating',
        
        # === HEART/PALPITATIONS ===
        'palpitations': 'palpitations',
        'heart palpitations': 'palpitations',
        'irregular heartbeat': 'palpitations',
        'heart racing': 'palpitations',
        'heart pounding': 'palpitations',
        'fast heartbeat': 'palpitations',
        'stomach pain': 'abdominal_pain',
        
        # === TREMOR/MUSCLE ===
        'tremor': 'tremor',
        'trembling': 'tremor',
        'shaking': 'tremor',
        'shaky': 'tremor',
        'muscle weakness': 'muscle_weakness',
        'weak muscles': 'muscle_weakness',
        'muscle pain': 'muscle_pain',
        'muscle ache': 'muscle_pain',
        
        # === DIZZINESS/BALANCE ===
        'dizziness': 'dizziness',
        'dizzy': 'dizziness',
        'vertigo': 'dizziness',
        'feeling dizzy': 'dizziness',
        'balance problems': 'balance_problems',
        'balance issues': 'balance_problems',
        'loss of balance': 'balance_problems',
        
        # === JOINTS ===
        'joint pain': 'joint_pain',
        'joint ache': 'joint_pain',
        'joint stiffness': 'joint_stiffness',
        'stiff joints': 'joint_stiffness',
        'morning stiffness': 'morning_stiffness',
        'swollen joints': 'swelling',
        
        # === VISION ===
        'blurred vision': 'blurred_vision',
        'vision blurry': 'blurred_vision',
        'eye blurry': 'blurred_vision',
        'sensitivity to light': 'sensitivity_to_light',
        'light sensitivity': 'sensitivity_to_light',
        'sensitive to light': 'sensitivity_to_light',
        
        # === BOWEL ISSUES ===
        'diarrhea': 'diarrhea',
        'loose stool': 'diarrhea',
        'loose stools': 'diarrhea',
        'watery stool': 'diarrhea',
        'constipation': 'constipation',
        'constipated': 'constipation',
        'unable to defecate': 'constipation',
        'cramping': 'cramping',
        'cramps': 'cramps',
        'stomach cramp': 'stomach_cramps',
        'belly cramp': 'stomach_cramps',
        'bloating': 'bloating',
        'bloated': 'bloating',
        'swelling in belly': 'bloating',
        
        # === LYMPH NODES ===
        'enlarged lymph nodes': 'enlarged_lymph_nodes',
        'swollen lymph nodes': 'enlarged_lymph_nodes',
        'swollen glands': 'enlarged_lymph_nodes',
        'lymphadenopathy': 'enlarged_lymph_nodes',
        
        # === COGNITIVE ===
        'confusion': 'confusion',
        'confused': 'confusion',
        'memory problems': 'memory_problems',
        'memory loss': 'memory_problems',
        'forgetfulness': 'memory_problems',
        'poor memory': 'memory_problems',
        
        # === MENTAL HEALTH ===
        'depression': 'depression',
        'sad': 'depression',
        'sadness': 'depression',
        'feeling depressed': 'depression',
        'anxiety': 'anxiety',
        'anxious': 'anxiety',
        'worry': 'anxiety',
        'worried': 'anxiety',
        'nervous': 'anxiety',
        
        # === NUMBNESS/TINGLING ===
        'numbness': 'numbness',
        'numb': 'numbness',
        'tingling': 'tingling',
        'pins and needles': 'tingling',
        'prickling': 'tingling',
        
        # === WEIGHT ===
        'weight loss': 'weight_loss',
        'losing weight': 'weight_loss',
        'rapid weight loss': 'weight_loss',
        'unintentional weight loss': 'weight_loss',
        
        # === OTHER ===
        'chills': 'chills',
        'feeling cold': 'chills',
        'cold shivers': 'chills',
        'shivering': 'chills',
        'wheezing': 'wheezing',
        'wheeze': 'wheezing',
        'difficulty swallowing': 'difficulty_swallowing',
        'hard to swallow': 'difficulty_swallowing',
        'swallowing difficulty': 'difficulty_swallowing',
        'sneezing': 'sneezing',
        'sneezes': 'sneezing',
        'sneezing a lot': 'sneezing',
        'warmth in joints': 'warmth_in_joints',
        'swelling': 'swelling',
        'swollen': 'swelling',
        'edema': 'swelling',
        'inflammation': 'swelling',
        'blood in sputum': 'blood_in_sputum',
        'coughing blood': 'blood_in_sputum',
        'hemoptysis': 'blood_in_sputum',
        'reduced mobility': 'reduced_mobility',
        'mobility issues': 'reduced_mobility',
        'muscle rigidity': 'muscle_rigidity',
        'stiff muscles': 'muscle_rigidity',
        'slowness of movement': 'slowness_of_movement',
        'slow movements': 'slowness_of_movement',
        'radiating pain': 'radiating_pain',
        'pain radiating': 'radiating_pain',
        'shooting pain': 'radiating_pain',
        'irregular bowel movements': 'irregular_bowel_movements',
        'abnormal bowel movements': 'irregular_bowel_movements',
        'mucus in stool': 'mucus_in_stool',
        'mucus production': 'mucus_production',
        'producing mucus': 'mucus_production',
        'excessive mucus': 'mucus_production',
        'mucus': 'mucus',
        'phlegm': 'mucus',
        'arm pain': 'arm_pain',
        'arm ache': 'arm_pain',
        'back pain': 'back_pain',
        'back ache': 'back_pain',
        'leg pain': 'leg_pain',
        'leg ache': 'leg_pain',
        'jaw pain': 'jaw_pain',
        'jaw ache': 'jaw_pain',
        'kidney pain': 'kidney_pain',
        'kidney ache': 'kidney_pain',
        'flank pain': 'kidney_pain',
    }

    # Rule-only symptom aliases for logic not covered by dataset symptoms
    RULE_SYMPTOM_ALIASES = {
        'frequent urination': 'polyuria',
        'burning urination': 'burning_micturition',
        'dysuria': 'burning_micturition',
        'increased thirst': 'polydipsia',
        'polydipsia': 'polydipsia',
        'polyuria': 'polyuria',
        'breathlessness': 'shortness_of_breath',
        'chest tightness': 'shortness_of_breath',
        'fast heartbeat': 'palpitations',
        'stomach pain': 'abdominal_pain',
    }

    # Priority rules for medical pattern matching (CRITICAL FEATURE)
    # Maps symptom patterns to priority diseases
    # NOTE: Only use symptoms that exist in the trained model's symptoms_list
    PRIORITY_RULES = {
        # Respiratory infections (fever + cough pattern)
        ('fever', 'cough'): ['Flu', 'Pneumonia', 'Bronchitis'],
        ('fever', 'persistent_cough'): ['Pneumonia', 'Tuberculosis'],
        
        # Dermatology (rash + itching pattern)
        ('rash', 'itching'): ['Chickenpox'],
        ('skin_rash', 'itching'): ['Chickenpox'],
        ('rash', 'scabs'): ['Chickenpox'],
        
        # Migraine (headache + nausea + light sensitivity)
        ('headache', 'nausea', 'sensitivity_to_light'): ['Migraine'],
        ('severe_headache', 'nausea', 'vomiting'): ['Migraine'],
        
        # Cardiac (chest pain + breathing difficulty)
        ('chest_pain', 'shortness_of_breath'): ['Heart Attack'],
        ('chest_pain', 'difficulty_breathing'): ['Heart Attack'],
        ('chest_pain', 'sweating'): ['Heart Attack'],
        
        # GI issues (nausea + vomiting + diarrhea)
        ('nausea', 'vomiting', 'diarrhea'): ['Gastroenteritis', 'Food Poisoning'],
        ('nausea', 'vomiting', 'stomach_cramps'): ['Gastroenteritis'],
        
        # Neurological (tremor + slowness)
        ('tremor', 'slowness_of_movement'): ['Parkinson Disease'],
        ('tremor', 'muscle_rigidity'): ['Parkinson Disease'],
        
        # Throat infection (sore throat + fever)
        ('sore_throat', 'fever'): ['Tonsillitis'],
        ('sore_throat', 'swollen_tonsils'): ['Tonsillitis'],
    }
    
    # Disease to doctor mapping
    DISEASE_TO_DOCTOR = {
        'Common Cold': 'General Physician',
        'Flu': 'General Physician',
        'Pneumonia': 'Pulmonologist',
        'Bronchitis': 'Pulmonologist',
        'Tuberculosis': 'Pulmonologist',
        'Dengue': 'Infectious Disease Specialist',
        'Chickenpox': 'Dermatologist',
        'Tonsillitis': 'ENT Specialist',
        'Gastroenteritis': 'Gastroenterologist',
        'Food Poisoning': 'Gastroenterologist',
        'Irritable Bowel Syndrome': 'Gastroenterologist',
        'Heart Attack': 'Cardiologist',
        'Arrhythmia': 'Cardiologist',
        'Migraine': 'Neurologist',
        'Concussion': 'Neurologist',
        'Parkinson Disease': 'Neurologist',
        'Arthritis': 'Rheumatologist',
        'Rheumatoid Arthritis': 'Rheumatologist',
        'Herniated Disc': 'Orthopedic Surgeon',
        'Lupus': 'Rheumatologist',
    }
    
    # Symptom to disease explanation mapping
    SYMPTOM_DISEASE_EXPLANATIONS = {
        ('Flu', 'fever'): 'Fever is a hallmark symptom of influenza as the immune system fights the virus',
        ('Flu', 'cough'): 'Cough is very common in flu, often accompanied by body aches',
        ('Common Cold', 'runny_nose'): 'Runny nose is a classic symptom of the common cold virus',
        ('Pneumonia', 'shortness_of_breath'): 'Difficulty breathing indicates lung inflammation (pneumonia)',
        ('Pneumonia', 'cough'): 'Persistent cough with respiratory infection suggests pneumonia',
        ('Heart Attack', 'chest_pain'): 'Chest pain is the primary warning sign of a heart attack - seek immediate medical attention',
        ('Migraine', 'headache'): 'Severe headaches are characteristic of migraine attacks',
        ('Gastroenteritis', 'diarrhea'): 'Diarrhea is a direct symptom of stomach infection (gastroenteritis)',
        ('Gastroenteritis', 'nausea'): 'Nausea and vomiting occur with food-borne illness',
    }
    
    # Disease to primary symptom categories mapping (for relevance filtering)
    DISEASE_SYMPTOM_MAPPING = {
        'Common Cold': {'runny_nose', 'sore_throat', 'cough', 'sneezing', 'fatigue', 'fever', 'body_ache'},
        'Flu': {'fever', 'cough', 'body_ache', 'fatigue', 'headache', 'sore_throat', 'runny_nose'},
        'Pneumonia': {'cough', 'fever', 'shortness_of_breath', 'chest_pain', 'fatigue', 'body_ache', 'chills'},
        'Bronchitis': {'cough', 'fatigue', 'shortness_of_breath', 'chest_pain', 'wheezing', 'fever', 'body_ache'},
        'Tuberculosis': {'cough', 'chest_pain', 'fever', 'night_sweats', 'fatigue', 'weight_loss', 'chills'},
        
        'Dengue': {'fever', 'headache', 'body_ache', 'muscle_pain', 'joint_pain', 'rash', 'fatigue'},
        'Chickenpox': {'rash', 'fever', 'fatigue', 'headache', 'body_ache', 'itching'},
        'Tonsillitis': {'sore_throat', 'fever', 'body_ache', 'fatigue', 'cough', 'difficulty_swallowing'},
        
        'Gastroenteritis': {'nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'fever', 'fatigue'},
        'Food Poisoning': {'nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'fever'},
        'Irritable Bowel Syndrome': {'abdominal_pain', 'diarrhea', 'cramping', 'nausea', 'bloating'},
        
        'Heart Attack': {'chest_pain', 'shortness_of_breath', 'sweating', 'palpitations', 'arm_pain', 'jaw_pain'},
        'Arrhythmia': {'palpitations', 'dizziness', 'shortness_of_breath', 'chest_pain', 'fatigue', 'sweating'},
        
        'Migraine': {'severe_headache', 'headache', 'nausea', 'vomiting', 'sensitivity_to_light', 'dizziness', 'blurred_vision'},
        'Concussion': {'severe_headache', 'dizziness', 'confusion', 'memory_problems', 'loss_of_consciousness', 'nausea'},
        'Parkinson Disease': {'tremor', 'muscle_weakness', 'stiffness', 'slow_movement', 'memory_problems'},
        
        'Arthritis': {'joint_pain', 'joint_stiffness', 'swelling', 'morning_stiffness', 'body_ache'},
        'Rheumatoid Arthritis': {'joint_pain', 'joint_stiffness', 'swelling', 'fatigue', 'morning_stiffness', 'fever'},
        'Herniated Disc': {'back_pain', 'leg_pain', 'numbness', 'muscle_weakness', 'arm_pain'},
        'Lupus': {'rash', 'joint_pain', 'fever', 'fatigue', 'chest_pain', 'headache'},
    }
    
    # MANDATORY SYMPTOMS - diseases REQUIRE these symptoms to be present
    MANDATORY_SYMPTOMS = {
        'Migraine': {'headache', 'severe_headache'},
        'Parkinson Disease': {'tremor', 'muscle_weakness', 'slowness_of_movement', 'muscle_rigidity'},
        'Heart Attack': {'chest_pain'},
        'Urinary Tract Infection': {'burning_micturition', 'polyuria'},
        'Asthma': {'wheezing', 'shortness_of_breath', 'difficulty_breathing'},
        'Bronchitis': {'cough'},  # Feature #16: Bronchitis REQUIRES cough to be present
        'Herniated Disc': {'back_pain'},
        'Concussion': {'severe_headache', 'dizziness', 'confusion'},
    }
    
    # SYMPTOM CATEGORIES for disease classification and scoring
    SYMPTOM_CATEGORIES = {
        'cardiac': {'chest_pain', 'sweating', 'dizziness', 'palpitations', 'arm_pain', 'jaw_pain', 'radiating_pain'},
        'respiratory': {'cough', 'fever', 'shortness_of_breath', 'difficulty_breathing', 'wheezing', 'breathlessness'},
        'gastro': {'vomiting', 'diarrhea', 'abdominal_pain', 'nausea', 'stomach_cramps', 'bloating'},
        'urinary': {'burning_micturition', 'polyuria', 'kidney_pain', 'flank_pain'},
        'infection': {'fever', 'chills', 'body_ache', 'fatigue', 'enlarged_lymph_nodes'},
        'allergy': {'sneezing', 'itching', 'runny_nose', 'skin_rash', 'rash'},
        'neurological': {'headache', 'severe_headache', 'dizziness', 'confusion', 'tremor', 'numbness'},
        'mental': {'fatigue', 'depression', 'anxiety', 'memory_problems', 'confusion'},
        'musculoskeletal': {'joint_pain', 'muscle_pain', 'back_pain', 'leg_pain', 'arm_pain', 'swelling', 'joint_stiffness'},
    }
    
    # ACUTE vs CHRONIC disease classification
    ACUTE_DISEASES = {
        'Common Cold', 'Flu', 'Pneumonia', 'Bronchitis', 'Dengue', 'Chickenpox',
        'Tonsillitis', 'Gastroenteritis', 'Food Poisoning', 'Heart Attack', 'Concussion',
        'Urinary Tract Infection', 'Asthma'
    }
    
    CHRONIC_DISEASES = {
        'Tuberculosis', 'Irritable Bowel Syndrome', 'Arrhythmia', 'Arthritis',
        'Rheumatoid Arthritis', 'Lupus', 'Parkinson Disease', 'Diabetes', 'Migraine'
    }
    
    # BODY LOCATION mapping
    BODY_LOCATION_MAPPING = {
        'chest': {'chest_pain', 'palpitations'},
        'head': {'headache', 'severe_headache', 'dizziness'},
        'throat': {'sore_throat', 'difficulty_swallowing', 'swollen_tonsils'},
        'chest/back': {'chest_pain', 'back_pain', 'radiating_pain'},
        'back': {'back_pain', 'kidney_pain', 'flank_pain'},
        'abdomen': {'abdominal_pain', 'stomach_cramps', 'nausea', 'diarrhea', 'vomiting'},
        'joints': {'joint_pain', 'joint_stiffness', 'swelling'},
        'muscles': {'muscle_pain', 'muscle_weakness', 'muscle_rigidity'},
        'localized': {'arm_pain', 'leg_pain', 'jaw_pain', 'kidney_pain'},
    }
    
    # DISEASE CATEGORIES
    DISEASE_CATEGORIES = {
        'respiratory': ['Common Cold', 'Flu', 'Pneumonia', 'Bronchitis', 'Tuberculosis', 'Asthma'],
        'cardiac': ['Heart Attack', 'Arrhythmia'],
        'gastro': ['Gastroenteritis', 'Food Poisoning', 'Irritable Bowel Syndrome'],
        'infection': ['Dengue', 'Chickenpox', 'Tonsillitis', 'Tuberculosis'],
        'neurological': ['Migraine', 'Concussion', 'Parkinson Disease'],
        'rheumatological': ['Arthritis', 'Rheumatoid Arthritis', 'Lupus'],
        'urinary': ['Urinary Tract Infection'],
        'other': ['Common Cold', 'Influenza'],
    }
    
    def __init__(self, model_dir: str = None):
        """
        Initialize the AI Predictor with trained models.
        
        Args:
            model_dir: Directory containing model files. 
                      Defaults to ml_model directory in project root.
        
        Raises:
            RuntimeError: If model files cannot be loaded
        """
        if model_dir is None:
            # Default to ml_model directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'ml_model')
        
        self.model_dir = model_dir
        self.model = None
        self.symptom_encoder = None
        self.disease_encoder = None
        self.symptoms_list = []
        
        self._load_models()
    
    def _load_models(self) -> None:
        """
        Load trained model and encoders from disk.
        
        Raises:
            RuntimeError: If required model files are not found
        """
        try:
            # Model file paths
            model_file = os.path.join(self.model_dir, 'dl_disease_model.pkl')
            symptom_encoder_file = os.path.join(self.model_dir, 'symptom_encoder.pkl')
            disease_encoder_file = os.path.join(self.model_dir, 'disease_encoder.pkl')
            symptom_list_file = os.path.join(self.model_dir, 'symptoms_list.json')
            
            # Validate files exist
            required_files = {
                'model': model_file,
                'symptom_encoder': symptom_encoder_file,
                'disease_encoder': disease_encoder_file,
                'symptom_list': symptom_list_file
            }
            
            missing_files = [name for name, path in required_files.items() if not os.path.exists(path)]
            if missing_files:
                raise FileNotFoundError(f"Missing model files: {', '.join(missing_files)}")
            
            # Load model
            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load encoders
            with open(symptom_encoder_file, 'rb') as f:
                self.symptom_encoder = pickle.load(f)
            
            with open(disease_encoder_file, 'rb') as f:
                self.disease_encoder = pickle.load(f)
            
            # Load symptoms list
            with open(symptom_list_file, 'r') as f:
                self.symptoms_list = json.load(f)
            
            print(f"[OK] AI Models loaded successfully ({len(self.symptoms_list)} symptoms)")
        
        except FileNotFoundError as e:
            raise RuntimeError(f"Model initialization failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading models: {e}")
    
    def _normalize_symptom(self, text: str) -> Optional[str]:
        """
        Normalize symptom text by checking variations and applying transformations.
        
        Args:
            text: Raw symptom text
            
        Returns:
            Normalized symptom name or None if not found
        """
        # Check direct variations mapping
        if text in self.SYMPTOM_VARIATIONS:
            return self.SYMPTOM_VARIATIONS[text]
        
        # Direct match
        if text in self.symptoms_list:
            return text
        
        return None
    
    def _fuzzy_match_symptom(self, text: str, threshold: float = 0.75) -> Optional[str]:
        """
        Find best matching symptom using fuzzy matching (SequenceMatcher).
        
        Args:
            text: Symptom text to match
            threshold: Similarity threshold (0-1), higher = stricter matching
            
        Returns:
            Best matching symptom or None
        """
        # Skip fuzzy matching for very short words to avoid false positives
        # (e.g., "arm" matching "arm_pain" is wrong if the symptom was just "arm")
        if len(text) < 3:
            return None
        
        # Skip common non-medical words
        common_words = {'and', 'the', 'a', 'an', 'or', 'i', 'me', 'my', 'have', 'has', 'is', 'am', 'are', 'got'}
        if text.lower() in common_words:
            return None
        
        best_match = None
        best_ratio = threshold
        
        for symptom in self.symptoms_list:
            ratio = SequenceMatcher(None, text.lower(), symptom.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = symptom
        
        return best_match
    
    def extract_symptoms(self, natural_language_input: str) -> List[str]:
        """
        Extract symptoms from natural language input with advanced hybrid matching.
        
        Uses 4-tier matching strategy:
        1. Multi-word phrase matching (e.g., "frequent urination" from SYMPTOM_VARIATIONS)
        2. Normalization/synonym mapping (variations like "high fever" → "fever")
        3. Direct matching against symptom list
        4. Fuzzy matching (partial match as final fallback)
        
        Args:
            natural_language_input: Raw user input (e.g., "I have fever and headache")
        
        Returns:
            List of matched symptoms (normalized to symptom list format)
        
        Example:
            >>> predictor.extract_symptoms("I have frequent urination and weight loss")
            ['weakness', 'weight_loss']  # frequent urination → weakness proxy
        """
        if not natural_language_input or not isinstance(natural_language_input, str):
            return []
        
        # Normalize input
        original_input = natural_language_input
        text_lower = natural_language_input.lower().strip()
        
        # Replace punctuation with spaces (but preserve word boundaries)
        text_lower = re.sub(r'[,;:\-—–]', ' ', text_lower)
        
        matched_symptoms = set()
        skip_words = {
            'pain', 'ache', 'aching', 'soreness', 'issue', 'problem',
            'symptom', 'symptoms', 'sick', 'ill', 'bad', 'good', 'ok', 'okay',
            'help', 'medical', 'condition', 'disease', 'health', 'body', 'having',
            'feel', 'feeling', 'have', 'has', 'had', 'been', 'very'
        }

        sorted_variations = sorted(self.SYMPTOM_VARIATIONS.items(), key=lambda item: len(item[0].split()), reverse=True)
        tokens = re.sub(r'\s+', ' ', text_lower).strip().split()
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

        words = []
        remaining_text = ''
        
        # Skip words that are too generic without context
        skip_words = {'pain', 'ache', 'aching', 'soreness', 'issue', 'problem', 
                     'symptom', 'symptoms', 'sick', 'ill', 'bad', 'good', 'ok', 'okay', 
                     'help', 'medical', 'condition', 'disease', 'health', 'body', 'having'}
        
        # =========================
        # TIER 2: Single-word normalization
        # =========================
        for word in words:
            if not word or len(word) < 2:
                continue
            
            if word.lower() in skip_words:
                continue
            
            # Try exact normalization
            normalized = self._normalize_symptom(word)
            if normalized:
                matched_symptoms.add(normalized)
                print(f"  TIER 2 MATCH: '{word}' (normalized) → '{normalized}'")
                continue
            
            # =========================
            # TIER 3: Direct symptom list matching
            # =========================
            if word in self.symptoms_list:
                matched_symptoms.add(word)
                print(f"  TIER 3 MATCH: '{word}' (direct) → '{word}'")
                continue
            
            # Try matching with underscore variant
            word_with_underscore = word.replace(' ', '_')
            if word_with_underscore in self.symptoms_list:
                matched_symptoms.add(word_with_underscore)
                print(f"  TIER 3 MATCH: '{word}' (underscore) → '{word_with_underscore}'")
                continue
            
            # =========================
            # TIER 4: Fuzzy matching (fallback)
            # =========================
            if len(word) >= 4:  # Only fuzzy match reasonably long words
                fuzzy_match = self._fuzzy_match_symptom(word, threshold=0.72)
                if fuzzy_match:
                    matched_symptoms.add(fuzzy_match)
                    print(f"  TIER 4 MATCH: '{word}' (fuzzy) → '{fuzzy_match}'")
        
        result = sorted(list(matched_symptoms))
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
        text_lower = re.sub(r'[,;:\-—–]', ' ', text_lower)
        text_lower = re.sub(r'\s+', ' ', text_lower).strip()
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
        """
        Validate extracted symptoms with flexible requirements.
        
        Requirements:
        - Minimum 1 valid symptom required (improved from 2)
        - All symptoms must be in the symptom list
        - No duplicates
        
        Args:
            symptoms: List of symptom strings
        
        Returns:
            Tuple of (is_valid, validation_message)
        """
        if not symptoms:
            return False, "Please provide at least 1 symptom (e.g., 'fever', 'headache and cough')"
        
        if len(symptoms) < 1:
            return False, f"Found only {len(symptoms)} symptom(s). Please provide at least 1 symptom."
        
        # Check if all symptoms are valid
        invalid_symptoms = [s for s in symptoms if s not in self.symptoms_list]
        if invalid_symptoms:
            return False, f"Invalid symptoms: {', '.join(invalid_symptoms)}. Please use valid symptoms."
        
        return True, "Symptoms validated successfully"
    
    def _create_symptom_vector(self, symptoms: List[str]) -> np.ndarray:
        """
        Create binary vector for symptoms using the symptom encoder.
        
        Args:
            symptoms: List of symptom strings
        
        Returns:
            Binary numpy array (1 x n_symptoms) where 1 = symptom present, 0 = absent
        """
        if not symptoms or not self.symptom_encoder:
            return np.zeros((1, len(self.symptoms_list)))
        
        try:
            # Use the encoder to transform symptoms
            vector = self.symptom_encoder.transform([symptoms])
            return vector
        except Exception as e:
            print(f"Warning: Error encoding symptoms, using fallback method: {e}")
            # Fallback: manual binary vector creation
            vector = np.zeros((1, len(self.symptoms_list)))
            for i, symptom in enumerate(self.symptoms_list):
                if symptom in symptoms:
                    vector[0, i] = 1
            return vector
    
    def _get_top_predictions(self, probabilities: np.ndarray, top_n: int = 5) -> List[Dict]:
        """
        Get top N disease predictions with confidence scores.
        
        Applies normalization to make confidence scores realistic and readable:
        - Highest prediction scaled to ~90% (using 0.9 factor)
        - Other predictions scaled proportionally
        - All values clamped between 5% and 95%
        
        Args:
            probabilities: Probability array from model.predict_proba
            top_n: Number of top predictions to return (default: 5)
        
        Returns:
            List of dicts with disease name and normalized confidence score
        """
        # Get indices of top probabilities
        top_indices = np.argsort(probabilities[0])[-top_n:][::-1]
        
        predictions = []
        raw_scores = []
        
        # First pass: collect raw scores for normalization
        for idx in top_indices:
            if probabilities[0][idx] > 0:  # Only include predictions with > 0 confidence
                disease_name = self.disease_encoder.inverse_transform([idx])[0]
                raw_score = float(probabilities[0][idx])
                raw_scores.append(raw_score)
                
                predictions.append({
                    'disease': disease_name,
                    'raw_score': raw_score
                })
        
        # Second pass: normalize scores using the highest probability
        if predictions and raw_scores:
            max_score = max(raw_scores)
            
            for pred in predictions:
                # Normalize relative to max: (score / max_score)
                # Apply scaling factor 0.85 for max ≈ 85%: * 0.85
                # Convert to percentage: * 100
                # Formula: (score / max_score) * 0.85 * 100
                normalized = (pred['raw_score'] / max_score) * 0.85 * 100
                
                # Clamp between 5% and 90% for professional appearance
                confidence = max(5.0, min(90.0, normalized))
                
                # Round to 1 decimal place for clean display
                confidence = round(confidence, 1)
                
                # Remove temporary raw_score, add normalized confidence
                del pred['raw_score']
                pred['confidence'] = confidence
        
        return predictions
    
    def _apply_priority_rules(self, predictions: List[Dict], symptoms: List[str]) -> List[Dict]:
        """
        Apply medical priority rules based on specific symptom patterns.
        
        Priority rules check for specific symptom combinations and boost
        relevant diseases to the top if they match the pattern.
        
        Examples:
        - "frequent_urination" + "increased_thirst" → boost "Diabetes"
        - "fever" + "cough" → boost "Flu"
        - "skin_rash" + "itching" → boost dermatology diseases
        
        Args:
            predictions: Current list of predictions
            symptoms: List of extracted symptoms
        
        Returns:
            Modified predictions with priority rules applied
        """
        if not predictions or not symptoms:
            return predictions
        
        symptom_set = set(symptoms)
        respiratory_symptoms = {'cough', 'fever', 'breathlessness', 'shortness_of_breath', 'wheezing'}
        cardiac_symptoms = {'chest_pain', 'sweating', 'dizziness', 'nausea', 'radiating_pain'}
        respiratory_score = len(symptom_set & respiratory_symptoms)
        cardiac_score = len(symptom_set & cardiac_symptoms)

        # Strong cardiac evidence required for Heart Attack prioritization
        if 'chest_pain' in symptom_set and symptom_set & {'sweating', 'radiating_pain', 'nausea', 'dizziness'}:
            for i, pred in enumerate(predictions):
                if pred['disease'] == 'Heart Attack':
                    boosted = pred.copy()
                    boosted['confidence'] = round(min(90.0, boosted['confidence'] * 1.25), 1)
                    print(f"DEBUG: Cardiac context rule boosted Heart Attack to {boosted['confidence']}%")
                    remaining = [p for j, p in enumerate(predictions) if j != i]
                    return [boosted] + remaining

        # Respiratory infection override: cough + fever + breathlessness
        if {'cough', 'fever'}.issubset(symptom_set) and ('breathlessness' in symptom_set or 'shortness_of_breath' in symptom_set):
            boosted = []
            others = []
            for pred in predictions:
                if pred['disease'] in ['Pneumonia', 'Bronchitis']:
                    new_pred = pred.copy()
                    new_pred['confidence'] = round(min(90.0, new_pred['confidence'] * 1.3), 1)
                    boosted.append(new_pred)
                    print(f"DEBUG: Respiratory infection rule boosted {pred['disease']} to {new_pred['confidence']}%")
                elif pred['disease'] == 'Heart Attack':
                    new_pred = pred.copy()
                    new_pred['confidence'] = round(max(5.0, new_pred['confidence'] * 0.6), 1)
                    others.append(new_pred)
                    print(f"DEBUG: Respiratory infection rule reduced Heart Attack to {new_pred['confidence']}%")
                else:
                    others.append(pred)
            if boosted:
                return boosted + others

        # Overall respiratory vs cardiac scoring
        if respiratory_score > cardiac_score:
            boosted = []
            others = []
            for pred in predictions:
                if pred['disease'] in ['Pneumonia', 'Bronchitis', 'Asthma']:
                    new_pred = pred.copy()
                    new_pred['confidence'] = round(min(90.0, new_pred['confidence'] * 1.2), 1)
                    boosted.append(new_pred)
                    print(f"DEBUG: Symptom score rule boosted respiratory {pred['disease']} to {new_pred['confidence']}%")
                elif pred['disease'] in ['Heart Attack', 'Arrhythmia']:
                    new_pred = pred.copy()
                    new_pred['confidence'] = round(max(5.0, new_pred['confidence'] * 0.7), 1)
                    others.append(new_pred)
                    print(f"DEBUG: Symptom score rule reduced cardiac {pred['disease']} to {new_pred['confidence']}%")
                else:
                    others.append(pred)
            if boosted:
                return boosted + others

        # Food Poisoning boost for vomiting + diarrhea
        if 'vomiting' in symptom_set and 'diarrhea' in symptom_set:
            for i, pred in enumerate(predictions):
                if pred['disease'] == 'Food Poisoning':
                    boosted = pred.copy()
                    boosted['confidence'] = round(min(90.0, boosted['confidence'] * 1.2), 1)
                    print(f"DEBUG: GI rule boosted Food Poisoning to {boosted['confidence']}%")
                    remaining = [p for j, p in enumerate(predictions) if j != i]
                    return [boosted] + remaining

        # Respiratory priority: boost Asthma/Bronchitis and reduce cardiac diseases if no chest pain
        if symptom_set & respiratory_symptoms and 'chest_pain' not in symptom_set:
            boosted = []
            others = []
            for pred in predictions:
                if pred['disease'] in ['Asthma', 'Bronchitis']:
                    new_pred = pred.copy()
                    new_pred['confidence'] = round(min(90.0, new_pred['confidence'] * 1.2), 1)
                    boosted.append(new_pred)
                    print(f"DEBUG: Respiratory rule boosted {pred['disease']} to {new_pred['confidence']}%")
                elif pred['disease'] in ['Heart Attack', 'Arrhythmia']:
                    new_pred = pred.copy()
                    new_pred['confidence'] = round(max(5.0, new_pred['confidence'] * 0.7), 1)
                    others.append(new_pred)
                    print(f"DEBUG: Respiratory rule reduced {pred['disease']} to {new_pred['confidence']}%")
                else:
                    others.append(pred)
            if boosted:
                return boosted + others
        
        # Feature #16: RULE PRIORITY ORDERING
        # Priority: 1. Required symptoms (MANDATORY)
        #           2. Strong indicators (itching, chest pain, urination issues)
        #           3. Category match
        #           4. General symptoms (fever, fatigue)
        # STRONG INDICATORS - Re-sort predictions based on priority
        strong_indicators = {'itching', 'chest_pain', 'burning_micturition', 'polyuria'}
        medications_with_strong = []
        other_medications = []
        
        for pred in predictions:
            disease = pred['disease']
            # Check if disease has strong indicator symptoms present
            strong_score = len(symptom_set & strong_indicators)
            if strong_score > 0 and disease in self.DISEASE_SYMPTOM_MAPPING:
                disease_strong = len(self.DISEASE_SYMPTOM_MAPPING[disease] & strong_indicators)
                if disease_strong > 0:  # This disease uses strong indicators
                    medications_with_strong.append(pred)
                    print(f"DEBUG: Feature #16 - {disease} prioritized (has strong indicators)")
                else:
                    other_medications.append(pred)
            else:
                other_medications.append(pred)
        
        if medications_with_strong:
            results = medications_with_strong + other_medications
            print(f"DEBUG: Feature #16 - Reordered by rule priority: strong indicators first")
            return results
        
        # Default pattern matching
        for symptom_pattern, priority_diseases in self.PRIORITY_RULES.items():
            if all(sym in symptom_set for sym in symptom_pattern):
                print(f"DEBUG: Priority rule matched: {symptom_pattern} → {priority_diseases}")
                modified_predictions = []
                priorities_found = []
                other_predictions = []
                for pred in predictions:
                    if pred['disease'] in priority_diseases:
                        boosted = pred.copy()
                        boosted['confidence'] = round(min(90.0, boosted['confidence'] * 1.2), 1)
                        priorities_found.append(boosted)
                        print(f"DEBUG: Boosted {pred['disease']} to {boosted['confidence']}%")
                    else:
                        other_predictions.append(pred)
                if priorities_found:
                    return priorities_found + other_predictions
        
        return predictions
    
    def _check_mandatory_symptoms(self, disease: str, symptoms: Set[str]) -> bool:
        """
        Check if a disease has all its mandatory symptoms present.
        
        Args:
            disease: Disease name
            symptoms: Set of detected symptoms
        
        Returns:
            True if disease has all mandatory symptoms or no mandatory requirements
        """
        if disease not in self.MANDATORY_SYMPTOMS:
            return True
        
        mandatory = self.MANDATORY_SYMPTOMS[disease]
        if not mandatory:
            return True
        
        # At least ONE mandatory symptom must be present
        return bool(mandatory & symptoms)
    
    def _categorize_symptoms(self, symptoms: List[str]) -> Dict[str, int]:
        """
        Categorize symptoms and calculate category scores.
        
        Args:
            symptoms: List of detected symptoms
        
        Returns:
            Dictionary mapping category names to match counts
        """
        symptom_set = set(symptoms)
        category_scores = {}
        
        for category, category_symptoms in self.SYMPTOM_CATEGORIES.items():
            score = len(symptom_set & category_symptoms)
            category_scores[category] = score
        
        return category_scores
    
    def _filter_acute_vs_chronic(self, predictions: List[Dict], symptoms: List[str]) -> List[Dict]:
        """
        Filter predictions based on acute vs chronic disease classification.
        
        If fever or chills present → prioritize acute diseases, remove chronic
        If no fever/chills → allow chronic diseases
        
        Args:
            predictions: List of predictions
            symptoms: List of detected symptoms
        
        Returns:
            Filtered predictions
        """
        symptom_set = set(symptoms)
        has_infection_marker = {'fever', 'chills'} & symptom_set
        
        if not has_infection_marker:
            return predictions
        
        # Has infection marker - remove obvious chronic diseases
        filtered = []
        for pred in predictions:
            if pred['disease'] not in ['Lupus', 'Rheumatoid Arthritis', 'Parkinson Disease', 'Arthritis']:
                filtered.append(pred)
        
        return filtered if filtered else predictions
    
    def _detect_injury_musculoskeletal(self, symptoms: List[str], user_input: str) -> Optional[Dict]:
        """
        Detect injury/musculoskeletal conditions based on localized pain + no systemic symptoms.
        
        Args:
            symptoms: List of detected symptoms
            user_input: Original user input
        
        Returns:
            Injury result dict if detected, None otherwise
        """
        symptom_set = set(symptoms)
        input_lower = user_input.lower()
        
        # Localized pain symptoms without systemic involvement
        localized_pain = {'arm_pain', 'leg_pain', 'back_pain', 'joint_pain', 'muscle_pain'}
        trauma_keywords = {'hit', 'fall', 'crash', 'blow', 'injury', 'accident', 'bump', 'struck', 'twisted', 'sprain', 'strain'}
        non_systemic = {'swelling'}
        
        has_localized = symptom_set & (localized_pain | non_systemic)
        has_systemic = {'fever', 'chills', 'infection'} & symptom_set
        has_trauma_context = any(word in input_lower for word in trauma_keywords)
        
        if has_localized and not has_systemic and (has_trauma_context or 'swelling' in symptom_set):
            injury_type = 'Muscle Injury'
            if 'swelling' in symptom_set:
                injury_type = 'Sprain or Strain'
            if 'arm_pain' in symptom_set or 'leg_pain' in symptom_set:
                if has_trauma_context:
                    injury_type = 'Possible Fracture'
            
            return {
                'symptoms': list(has_localized),
                'severity': 'Medium',
                'predictions': [{
                    'disease': injury_type,
                    'confidence': 85.0,
                    'explanation': f'Detected localized pain with swelling/trauma context. Likely musculoskeletal injury.',
                    'doctor': 'Orthopedic Surgeon'
                }],
                'input_validation': {
                    'valid': True,
                    'message': 'Musculoskeletal injury detected'
                }
            }
        
        return None
    
    def _filter_by_body_location(self, predictions: List[Dict], symptoms: List[str]) -> List[Dict]:
        """
        Filter diseases based on body location matching.
        
        Examples:
        - If no headache → remove Migraine
        - If no vomiting/diarrhea → remove gastro diseases
        
        Args:
            predictions: List of predictions
            symptoms: List of detected symptoms
        
        Returns:
            Filtered predictions
        """
        symptom_set = set(symptoms)
        filtered = []
        
        for pred in predictions:
            disease = pred['disease']
            disease_symptoms = self.DISEASE_SYMPTOM_MAPPING.get(disease, set())
            
            # Check for required body location symptoms
            if disease == 'Migraine' and 'headache' not in symptom_set and 'severe_headache' not in symptom_set:
                continue
            
            if disease in ['Gastroenteritis', 'Food Poisoning', 'Irritable Bowel Syndrome']:
                if not {'vomiting', 'diarrhea', 'abdominal_pain', 'nausea'} & symptom_set:
                    continue
            
            if disease == 'Heart Attack' and 'chest_pain' not in symptom_set:
                continue
            
            if disease in ['Arthritis', 'Rheumatoid Arthritis']:
                if not {'joint_pain', 'joint_stiffness', 'swelling'} & symptom_set:
                    continue
            
            filtered.append(pred)
        
        return filtered if filtered else predictions
    
    def _apply_strict_category_filtering(self, predictions: List[Dict], category_scores: Dict[str, int], symptoms: List[str]) -> List[Dict]:
        """
        Apply STRICT category filtering: only keep diseases from primary category.
        
        After category scoring, identifies the PRIMARY (highest-scoring) category
        and removes ALL diseases from unrelated categories.
        
        Exceptions: Diseases with strong overlapping symptoms across categories
        (e.g., Migraine has neurological + cardiac overlap in some cases)
        
        Args:
            predictions: List of disease predictions
            category_scores: Dictionary of category → symptom count
            symptoms: List of extracted symptoms
        
        Returns:
            Filtered predictions containing only primary category diseases
        """
        if not predictions or not category_scores:
            return predictions
        
        # Find primary category (highest score)
        primary_category = max(category_scores, key=category_scores.get)
        primary_score = category_scores[primary_category]
        
        if primary_score == 0:
            return predictions
        
        print(f"DEBUG: Primary category: {primary_category} (score: {primary_score})")
        
        # Map diseases to their primary categories
        disease_to_category = {}
        for category, diseases in self.DISEASE_CATEGORIES.items():
            for disease in diseases:
                if disease not in disease_to_category:
                    disease_to_category[disease] = category
        
        # Filter: keep only diseases from primary category or with critical cross-category symptoms
        symptom_set = set(symptoms)
        filtered = []
        removed = []
        
        for pred in predictions:
            disease = pred['disease']
            disease_category = disease_to_category.get(disease, 'other')
            
            # Rule 1: Keep if from primary category
            if disease_category == primary_category:
                filtered.append(pred)
                print(f"DEBUG: KEEP {disease} (primary category)")
                continue
            
            # Rule 2: Allow cross-category overlap for diseases with STRONG symptom overlap
            # Example: Migraine (neurological) can have cardiac symptoms (nausea, palpitations)
            # Example: Heart Attack (cardiac) can have respiratory symptoms (breathlessness)
            
            disease_symptoms = self.DISEASE_SYMPTOM_MAPPING.get(disease, set())
            overlap_count = len(symptom_set & disease_symptoms)
            overlap_percentage = overlap_count / len(disease_symptoms) if disease_symptoms else 0
            
            # Allow cross-category diseases if > 60% symptom overlap AND confidence is high
            if overlap_percentage > 0.6 and pred['confidence'] >= 70:
                filtered.append(pred)
                print(f"DEBUG: KEEP {disease} (cross-category overlap: {overlap_percentage:.1%})")
                continue
            
            # Rule 3: Remove all other diseases
            removed.append(disease)
            print(f"DEBUG: REMOVE {disease} (wrong category: {disease_category})")
        
        # Ensure we always return at least 1 prediction
        return filtered if filtered else predictions[:1]
    
    def _apply_category_based_prioritization(self, predictions: List[Dict], category_scores: Dict[str, int]) -> List[Dict]:
        """
        Prioritize diseases based on strongest matching symptom category.
        
        Args:
            predictions: List of predictions
            category_scores: Dictionary of category → score counts
        
        Returns:
            Reordered predictions by category match strength
        """
        if not category_scores or not predictions:
            return predictions
        
        # Get the strongest category
        strongest_category = max(category_scores, key=category_scores.get)
        strongest_score = category_scores[strongest_category]
        
        if strongest_score == 0:
            return predictions
        
        # Map diseases to their primary categories
        disease_categories = {}
        for category, diseases in self.DISEASE_CATEGORIES.items():
            for disease in diseases:
                if disease not in disease_categories:
                    disease_categories[disease] = category
        
        # Sort: prioritize diseases from strongest category
        prioritized = []
        other = []
        
        for pred in predictions:
            if disease_categories.get(pred['disease']) == strongest_category:
                prioritized.append(pred)
            else:
                other.append(pred)
        
        return prioritized + other
    
    def _smart_disease_filtering(self, predictions: List[Dict], symptoms: List[str], user_input: str = "") -> List[Dict]:
        """
        Apply comprehensive disease filtering rules:
        - Remove diseases without required symptoms
        - Remove diseases not matching detected categories
        - Apply body location logic
        - Apply context filtering
        
        Args:
            predictions: List of predictions
            symptoms: List of detected symptoms
            user_input: Original user input
        
        Returns:
            Filtered predictions
        """
        if not predictions or not symptoms:
            return predictions
        
        symptom_set = set(symptoms)
        filtered = []
        
        for pred in predictions:
            disease = pred['disease']
            
            # Rule 1: Check mandatory symptoms (Feature #16: Includes bronchitis cough requirement)
            if not self._check_mandatory_symptoms(disease, symptom_set):
                if disease == 'Bronchitis':
                    print(f"DEBUG: Feature #16 - Removed Bronchitis - MANDATORY cough symptom missing")
                else:
                    print(f"DEBUG: Removed {disease} - missing mandatory symptoms")
                continue
            
            # Rule 2: Minimum relevance check
            relevance = self._calculate_symptom_relevance(disease, symptoms)
            if relevance < 0.1:
                print(f"DEBUG: Removed {disease} - insufficient symptom relevance ({relevance:.1%})")
                continue
            
            filtered.append(pred)
        
        # Rule 3: Apply body location filtering
        filtered = self._filter_by_body_location(filtered, symptoms)
        
        # Rule 4: Apply acute vs chronic filtering
        filtered = self._filter_acute_vs_chronic(filtered, symptoms)
        
        return filtered if filtered else predictions[:1]
    
    def _detect_severity(self, symptoms: List[str], top_disease: str) -> str:
        """
        Detect severity based on CRITICAL SYMPTOMS ONLY - not disease type.
        
        HIGH severity ONLY if:
        - Chest pain, breathing difficulty, or loss of consciousness
        
        MEDIUM severity if:
        - Has moderate symptoms like fever with other signs
        - Not critical but warrants medical attention
        
        LOW severity if:
        - Mild symptoms only (cold, minor ache)
        
        Args:
            symptoms: List of extracted symptoms
            top_disease: Top predicted disease name
        
        Returns:
            Severity level: 'Low', 'Medium', or 'High'
        """
        # CRITICAL SYMPTOMS = HIGH SEVERITY
        critical_symptoms = {
            'chest_pain', 'shortness_of_breath', 'difficulty_breathing', 
            'loss_of_consciousness', 'severe_headache'
        }
        
        for symptom in symptoms:
            if symptom in critical_symptoms:
                return 'High'
        
        # MODERATE SYMPTOMS - require at least 2 to be MEDIUM
        moderate_symptoms = {
            'fever', 'persistent_cough', 'cough', 'severe_vomiting', 
            'abdominal_pain', 'headache', 'chills', 'muscle_pain'
        }
        
        moderate_symptom_count = sum(1 for s in symptoms if s in moderate_symptoms)
        if moderate_symptom_count >= 2:
            return 'Medium'
        
        # Single moderate symptom or mild symptoms = LOW
        return 'Low'
    
    def _calculate_symptom_relevance(self, disease: str, symptoms: List[str]) -> float:
        """
        Calculate how relevant detected symptoms are to a disease.
        
        Args:
            disease: Disease name to check
            symptoms: List of detected symptoms
        
        Returns:
            Relevance score (0-1): proportion of detected symptoms matching the disease
        """
        if disease not in self.DISEASE_SYMPTOM_MAPPING or not symptoms:
            return 0.0
        
        disease_symptoms = self.DISEASE_SYMPTOM_MAPPING[disease]
        detected_set = set(symptoms)
        
        # Calculate overlap
        matching = len(detected_set & disease_symptoms)
        total_detected = len(detected_set)
        
        if total_detected == 0:
            return 0.0
        
        # Relevance = percentage of detected symptoms that match this disease
        relevance = matching / total_detected
        return relevance
    
    def _apply_symptom_based_correction(self, predictions: List[Dict], symptoms: List[str], user_input: str = "") -> List[Dict]:
        """
        Apply symptom-based filtering and ranking:
        
        1. Filter diseases with zero symptom match (complete irrelevance)
        2. Rerank using pattern matching for common diseases
        3. Remove trauma-unrelated diseases
        4. Ensure output is medically logical
        
        Args:
            predictions: List of disease predictions with confidence
            symptoms: Extracted symptoms from user input
            user_input: Original user input text
        
        Returns:
            Filtered and reordered predictions list
        """
        if not predictions or not symptoms:
            return predictions
        
        # Create a copy to modify
        corrected = predictions.copy()
        symptom_set = set(symptoms)
        user_input_lower = user_input.lower()
        
        # STEP 1: Remove completely irrelevant diseases (zero symptom matching)
        # Calculate relevance for each disease
        filtered_predictions = []
        for pred in corrected:
            disease = pred['disease']
            relevance = self._calculate_symptom_relevance(disease, symptoms)
            
            # Keep if:
            # 1. It's the top prediction (give benefit of doubt), OR
            # 2. It has at least some symptom match (relevance > 0), OR  
            # 3. It has at least 0.25 relevance (some symptoms match)
            is_top_pred = (len(filtered_predictions) == 0)
            has_reasonable_match = relevance > 0.0
            
            if is_top_pred or has_reasonable_match:
                filtered_predictions.append(pred)
                print(f"DEBUG: Keeping {disease} (relevance: {relevance:.2f})")
            else:
                print(f"DEBUG: FILTERED OUT {disease} (no match, relevance: {relevance:.2f})")
        
        corrected = filtered_predictions if filtered_predictions else predictions[:1]
        
        # Filtering hard rules that require explicit symptoms
        if corrected:
            filtered = []
            for pred in corrected:
                if pred['disease'] == 'Parkinson Disease' and not symptom_set & {'tremor', 'muscle_weakness', 'stiffness', 'slowness_of_movement'}:
                    print('DEBUG: Removed Parkinson Disease (no tremor/movement symptoms)')
                    continue
                if pred['disease'] == 'Lupus' and not symptom_set & {'joint_pain', 'swelling', 'fatigue', 'rash', 'chest_pain', 'headache'}:
                    print('DEBUG: Removed Lupus (no joint/chronic symptoms)')
                    continue
                if pred['disease'] == 'Heart Attack' and 'chest_pain' not in symptom_set:
                    print('DEBUG: Removed Heart Attack (no chest pain)')
                    continue
                filtered.append(pred)
            corrected = filtered if filtered else corrected

        # STEP 2: Pattern-based ranking optimization
        
        # Pattern 1: Migraine Pattern
        migraine_indicators = {'headache', 'severe_headache', 'nausea', 'blurred_vision', 'sensitivity_to_light', 'dizziness', 'vomiting'}
        migraine_match = len(symptom_set & migraine_indicators) >= 2
        
        if migraine_match:
            for i, pred in enumerate(corrected):
                if pred['disease'] == 'Migraine' and i > 0:
                    # Only boost if Migraine is in top 2
                    if i < 2:
                        migraine = corrected.pop(i)
                        corrected.insert(0, migraine)
                        migraine['confidence'] = round(min(90.0, migraine['confidence'] * 1.15), 1)
                        print(f"DEBUG: Boosted Migraine to #1 ({migraine['confidence']}%)")
                    break
        
        # Pattern 2: Cold Pattern
        cold_indicators = {'runny_nose', 'sore_throat', 'cough', 'sneezing', 'fatigue'}
        cold_match = len(symptom_set & cold_indicators) >= 3
        
        if cold_match:
            for i, pred in enumerate(corrected):
                if pred['disease'] == 'Common Cold' and i > 0:
                    if i < 2:
                        cold = corrected.pop(i)
                        corrected.insert(0, cold)
                        cold['confidence'] = round(min(90.0, cold['confidence'] * 1.1), 1)
                        print(f"DEBUG: Boosted Common Cold to #1 ({cold['confidence']}%)")
                    break
        
        # Pattern 3: GI/Gastroenteritis Pattern
        gi_indicators = {'nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'cramping'}
        gi_match = len(symptom_set & gi_indicators) >= 3
        
        if gi_match:
            for i, pred in enumerate(corrected):
                if pred['disease'] in ['Gastroenteritis', 'Food Poisoning'] and i > 0:
                    if i < 2:
                        gi = corrected.pop(i)
                        corrected.insert(0, gi)
                        gi['confidence'] = round(min(90.0, gi['confidence'] * 1.15), 1)
                        print(f"DEBUG: Boosted {gi['disease']} to #1 ({gi['confidence']}%)")
                    break
        
        # Pattern 4: Cardiac Pattern
        cardiac_indicators = {'chest_pain', 'shortness_of_breath', 'sweating', 'palpitations', 'arm_pain', 'jaw_pain'}
        cardiac_match = len(symptom_set & cardiac_indicators) >= 2
        
        if cardiac_match:
            for i, pred in enumerate(corrected):
                if pred['disease'] in ['Heart Attack', 'Arrhythmia'] and i > 0:
                    if i < 2:
                        cardiac = corrected.pop(i)
                        corrected.insert(0, cardiac)
                        cardiac['confidence'] = round(min(90.0, cardiac['confidence'] * 1.15), 1)
                        print(f"DEBUG: Boosted {cardiac['disease']} to #1 ({cardiac['confidence']}%)")
                    break
        
        # STEP 3: Trauma Logic - Remove Concussion if no trauma context
        trauma_words = {'hit', 'fall', 'crash', 'blow', 'injury', 'head injury', 'accident', 'bump', 'struck', 'knocked'}
        has_trauma_context = any(word in user_input_lower for word in trauma_words)
        trauma_indicators = {'confusion', 'memory_problems', 'loss_of_consciousness', 'balance_problems'}
        has_trauma_symptoms = len(symptom_set & trauma_indicators) > 0
        
        if not has_trauma_context and not has_trauma_symptoms:
            corrected = [p for p in corrected if p['disease'] != 'Concussion']
            if not corrected:
                # If we removed Concussion and nothing left, restore one
                corrected = predictions[:1]
            print(f"DEBUG: Removed Concussion (no trauma context)")
        
        # Ensure we always return at least 1 prediction
        return corrected if corrected else predictions[:1]
    
    def predict(self, natural_language_input: str) -> Dict:
        """
        Predict disease from natural language symptom description.
        
        Hybrid AI Process:
        1. Extract symptoms using enhanced NLP
        2. Validate symptoms
        3. Create binary vector
        4. Get predictions using model.predict_proba()
        5. Extract top 5 diseases with confidence scores
        6. Apply medical priority rules (CRITICAL)
        7. Apply symptom-based correction and filtering
        8. Detect severity
        9. Keep only top 3 relevant diseases
        10. Generate explanations
        
        Args:
            natural_language_input: User-provided symptom description
                                   e.g., "I have frequent urination and increased thirst"
        
        Returns:
            Dictionary with structure:
            {
                "symptoms": ["fever", "headache"],
                "severity": "Low" | "Medium" | "High",
                "predictions": [
                    {"disease": "Flu", "confidence": 85.5, "explanation": "..."},
                    ...
                ],
                "input_validation": {
                    "valid": True,
                    "message": "Symptoms validated successfully"
                }
            }
        
        Raises:
            RuntimeError: If model is not properly initialized
        """
        if not self.model or not self.disease_encoder:
            raise RuntimeError("AI model not initialized. Please check model files.")
        
        try:
            # Step 1: Extract symptoms using enhanced NLP
            symptoms = self.extract_symptoms(natural_language_input)
            print(f"DEBUG: Extracted symptoms: {symptoms}")
            
            # Step 1.5: INJURY/MUSCULOSKELETAL DETECTION (Early check)
            injury_result = self._detect_injury_musculoskeletal(symptoms, natural_language_input)
            if injury_result:
                print(f"DEBUG: Injury/musculoskeletal condition detected")
                return injury_result
            
            # Step 1.6: RULE-BASED OVERRIDES AND WEAK INPUT HANDLING
            input_lower = natural_language_input.lower()
            rule_symptoms = self._extract_rule_symptoms(natural_language_input)
            combined_symptoms = symptoms + [s for s in rule_symptoms if s not in symptoms]
            print(f"DEBUG: Rule symptoms: {rule_symptoms}")
            print(f"DEBUG: Combined symptoms: {combined_symptoms}")

            # Weak input handling: not enough explicit symptoms for a confident prediction
            if len(combined_symptoms) <= 1:
                return {
                    'symptoms': combined_symptoms,
                    'severity': 'Low',
                    'predictions': [{
                        'disease': 'Insufficient Data',
                        'confidence': 30.0,
                        'explanation': 'Insufficient symptoms for accurate prediction. Please enter more symptoms.',
                        'doctor': 'General Physician'
                    }],
                    'input_validation': {
                        'valid': False,
                        'message': 'Insufficient symptoms for accurate prediction',
                        'suggestion': 'Please enter more symptoms'
                    }
                }

            # Diabetes override
            has_diabetes = (
                ('polyuria' in rule_symptoms or 'frequent urination' in input_lower or 'urinating frequently' in input_lower or 'urinate frequently' in input_lower) and
                ('polydipsia' in rule_symptoms or 'increased thirst' in input_lower or 'polydipsia' in input_lower or 'very thirsty' in input_lower or 'always thirsty' in input_lower)
            )
            if has_diabetes:
                diabetes_symptoms_found = []
                if 'polyuria' in rule_symptoms or 'frequent urination' in input_lower or 'urinating frequently' in input_lower or 'urinate frequently' in input_lower:
                    diabetes_symptoms_found.append('polyuria')
                if 'polydipsia' in rule_symptoms or 'increased thirst' in input_lower or 'polydipsia' in input_lower or 'very thirsty' in input_lower or 'always thirsty' in input_lower:
                    diabetes_symptoms_found.append('polydipsia')
                if 'weight_loss' in symptoms or 'weight loss' in input_lower or 'losing weight' in input_lower:
                    diabetes_symptoms_found.append('weight_loss')
                if 'fatigue' in symptoms or 'fatigue' in input_lower or 'tired' in input_lower:
                    diabetes_symptoms_found.append('fatigue')
                diabetes_result = {
                    'symptoms': diabetes_symptoms_found,
                    'severity': 'Medium',
                    'predictions': [{
                        'disease': 'Diabetes',
                        'confidence': 90.0,
                        'explanation': f'Prediction based on detected symptoms: {", ".join(diabetes_symptoms_found)}.',
                        'doctor': 'Endocrinologist'
                    }],
                    'input_validation': {
                        'valid': True,
                        'message': 'Symptoms validated successfully'
                    }
                }
                print(f"DEBUG: Rule-based override triggered - Diabetes detected")
                return diabetes_result

            # UTI override
            has_uti = (
                'burning_micturition' in rule_symptoms or 'burning urination' in input_lower or 'dysuria' in input_lower
            ) and (
                'polyuria' in rule_symptoms or 'frequent urination' in input_lower or 'polyuria' in input_lower
            )
            if has_uti:
                uti_symptoms = ['burning_micturition', 'polyuria']
                uti_result = {
                    'symptoms': uti_symptoms,
                    'severity': 'Medium',
                    'predictions': [{
                        'disease': 'Urinary Tract Infection',
                        'confidence': 90.0,
                        'explanation': 'Prediction based on detected symptoms: burning urination and frequent urination.',
                        'doctor': 'Urologist'
                    }],
                    'input_validation': {
                        'valid': True,
                        'message': 'Symptoms validated successfully'
                    }
                }
                print(f"DEBUG: Rule-based override triggered - UTI detected")
                return uti_result

            # Asthma override
            has_asthma = (
                ('shortness_of_breath' in combined_symptoms or 'breathlessness' in input_lower or 'chest tightness' in input_lower) and
                'wheezing' in combined_symptoms
            )
            if has_asthma:
                asthma_symptoms = ['shortness_of_breath', 'wheezing']
                asthma_result = {
                    'symptoms': asthma_symptoms,
                    'severity': 'Medium',
                    'predictions': [{
                        'disease': 'Asthma',
                        'confidence': 90.0,
                        'explanation': 'Prediction based on detected symptoms: shortness of breath and wheezing.',
                        'doctor': 'Pulmonologist'
                    }],
                    'input_validation': {
                        'valid': True,
                        'message': 'Symptoms validated successfully'
                    }
                }
                print(f"DEBUG: Rule-based override triggered - Asthma detected")
                return asthma_result

            # Feature #16: SYMPTOM CONFLICT RESOLUTION - Allergy vs Common Cold Disambiguation
            # Rule: ITCHING has highest priority (indicates allergy)
            # Fever can COEXIST with allergy → return both with allergy as PRIMARY
            has_itching = 'itching' in symptoms or 'itching' in input_lower or 'itchy' in input_lower
            has_sneezing = 'sneezing' in symptoms or 'sneezing' in input_lower or 'sneezes' in input_lower
            has_runny_nose = 'runny_nose' in symptoms or 'runny nose' in input_lower or 'nasal congestion' in input_lower
            has_fever = 'fever' in symptoms or 'fever' in input_lower or 'high fever' in input_lower
            
            # CONFLICT RESOLUTION: Allergy priority rule (Feature #16)
            # CASE 1: Itching present (with or WITHOUT fever) → ALLERGY is top diagnosis
            if has_itching:
                allergy_symptoms_found = []
                if has_itching:
                    allergy_symptoms_found.append('itching')
                if has_sneezing:
                    allergy_symptoms_found.append('sneezing')
                if has_runny_nose:
                    allergy_symptoms_found.append('runny_nose')
                
                # Need at least 2 allergy symptoms OR itching + sneezing/runny_nose
                if len(allergy_symptoms_found) >= 2 or (has_itching and (has_sneezing or has_runny_nose)):
                    
                    # CASE 1A: Allergy WITHOUT fever (clear allergy)
                    if not has_fever:
                        allergy_result = {
                            'symptoms': allergy_symptoms_found,
                            'severity': 'Low',
                            'predictions': [{
                                'disease': 'Allergic Rhinitis',
                                'confidence': 90.0,
                                'explanation': f'Allergy detected based on symptoms: {", ".join(allergy_symptoms_found)}. Absence of fever indicates allergic reaction rather than infection.',
                                'doctor': 'Allergist'
                            }],
                            'input_validation': {
                                'valid': True,
                                'message': 'Symptoms validated successfully'
                            }
                        }
                        print(f"DEBUG: Feature #16 - Allergy (No fever) detected")
                        return allergy_result
                    
                    # CASE 1B: Allergy WITH fever (coexisting - Feature #16 conflict resolution)
                    # IMPORTANT: ITCHING priority > fever, so keep allergy as PRIMARY with cold/flu secondary
                    else:
                        print(f"DEBUG: Feature #16 - CONFLICT RESOLUTION: Allergy + Fever detected")
                        print(f"DEBUG: ITCHING priority > fever - keeping allergy as PRIMARY prediction")
                        
                        # Create allergy prediction with note about fever
                        allergy_pred = {
                            'disease': 'Allergic Rhinitis',
                            'confidence': 85.0,  # Slightly lower due to fever complication
                            'explanation': f'Allergy detected based on symptoms: {", ".join(allergy_symptoms_found)}. NOTE: Fever is present - possible coexisting viral infection. Recommend allergy treatment with monitoring.',
                            'doctor': 'Allergist'
                        }
                        
                        # Return allergy as PRIMARY + cold/flu as SECONDARY in predictions list
                        allergy_with_fever_result = {
                            'symptoms': allergy_symptoms_found + ['fever'],
                            'severity': 'Medium',
                            'predictions': [
                                allergy_pred,  # PRIMARY: Allergy (itching priority)
                                {
                                    'disease': 'Common Cold or Flu',
                                    'confidence': 75.0,  # SECONDARY: Fever-based cold/flu
                                    'explanation': 'Fever present suggests possible concurrent viral infection',
                                    'doctor': 'General Physician'
                                }
                            ],
                            'conflict_resolution': {
                                'primary': 'Allergic Rhinitis (ITCHING priority overrides fever)',
                                'secondary': 'Common Cold/Flu (fever-based)',
                                'recommendation': 'Treat allergy as primary; monitor for cold/flu escalation'
                            },
                            'input_validation': {
                                'valid': True,
                                'message': 'Coexisting symptoms detected - both conditions possible'
                            }
                        }
                        return allergy_with_fever_result

            # Step 2: Validate symptoms
            is_valid, validation_msg = self.validate_symptoms(symptoms)
            print(f"DEBUG: Validation result: valid={is_valid}, msg={validation_msg}")
            
            # Step 3: Create symptom vector
            symptom_vector = self._create_symptom_vector(symptoms)
            
            # Step 4: Get predictions using model.predict_proba()
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(symptom_vector)
            else:
                # Fallback: if model doesn't support predict_proba
                predictions = self.model.predict(symptom_vector)
                probabilities = np.eye(len(self.disease_encoder.classes_))[predictions[0]].reshape(1, -1)
            
            # Step 5: Get top 5 predictions (for more comprehensive analysis)
            top_predictions = self._get_top_predictions(probabilities, top_n=5)
            print(f"DEBUG: Top 5 predictions: {top_predictions}")
            
            # Step 6: APPLY MEDICAL PRIORITY RULES (CRITICAL FEATURE)
            top_predictions = self._apply_priority_rules(top_predictions, symptoms)
            print(f"DEBUG: After priority rules: {top_predictions}")
            
            # Step 7: APPLY SYMPTOM-BASED CORRECTION AND FILTERING
            top_predictions = self._apply_symptom_based_correction(top_predictions, symptoms, natural_language_input)
            print(f"DEBUG: Corrected predictions: {top_predictions}")
            
            # Step 7.5: APPLY SMART DISEASE FILTERING (mandatory symptoms, body location, acute/chronic)
            top_predictions = self._smart_disease_filtering(top_predictions, symptoms, natural_language_input)
            print(f"DEBUG: After smart filtering: {top_predictions}")
            
            # Step 7.6: APPLY CATEGORY-BASED PRIORITIZATION
            category_scores = self._categorize_symptoms(symptoms)
            print(f"DEBUG: Symptom category scores: {category_scores}")
            top_predictions = self._apply_category_based_prioritization(top_predictions, category_scores)
            print(f"DEBUG: After category prioritization: {top_predictions}")
            
            # Step 7.7: APPLY STRICT CATEGORY FILTERING (FINAL FIX)
            # Only keep diseases from primary category, remove all unrelated ones
            top_predictions = self._apply_strict_category_filtering(top_predictions, category_scores, symptoms)
            print(f"DEBUG: After strict category filtering: {top_predictions}")
            
            # Step 7.8: FALLBACK INTELLIGENCE - if no predictions remain, restore and assign low confidence
            if not top_predictions:
                print(f"DEBUG: No predictions after filtering, applying fallback logic")
                # Use original predictions but mark as low confidence
                if 'top_predictions' in locals():
                    # Get the highest confidence original prediction
                    top_predictions = [{
                        'disease': 'Symptoms unclear or insufficient data',
                        'confidence': 25.0,
                        'explanation': 'Symptoms do not clearly match any disease in the database. Please provide more symptoms or consult a doctor.',
                        'doctor': 'General Physician'
                    }]
                else:
                    top_predictions = [{
                        'disease': 'Insufficient Data',
                        'confidence': 30.0,
                        'explanation': 'Unable to make a reliable prediction. Please provide more detailed symptoms.',
                        'doctor': 'General Physician'
                    }]
            
            # Step 8: Keep only top 3 for final output
            top_predictions = top_predictions[:3]
            
            # Step 9: Detect severity
            top_disease = top_predictions[0]['disease'] if top_predictions else 'Unknown'
            severity = self._detect_severity(symptoms, top_disease)
            
            # Step 10: Generate explanations for each prediction
            for pred in top_predictions:
                pred['explanation'] = self._generate_explanation(pred['disease'], symptoms)
                pred['doctor'] = self.get_recommended_doctor(pred['disease'])
            
            # Build response
            result = {
                'symptoms': symptoms,
                'severity': severity,
                'predictions': top_predictions,
                'input_validation': {
                    'valid': is_valid,
                    'message': validation_msg
                }
            }
            
            return result
        
        except Exception as e:
            # Return structured error response
            return {
                'symptoms': [],
                'severity': 'Unknown',
                'predictions': [],
                'input_validation': {
                    'valid': False,
                    'message': f'Prediction failed: {str(e)}'
                },
                'error': str(e)
            }
    
    def get_symptom_suggestions(self, partial_text: str, limit: int = 10) -> List[str]:
        """
        Get symptom suggestions based on partial text input.
        
        Args:
            partial_text: Partial symptom name or word
            limit: Maximum number of suggestions
        
        Returns:
            List of matching symptom suggestions
        """
        if not partial_text or not isinstance(partial_text, str):
            return []
        
        query = partial_text.lower().strip()
        suggestions = [
            symptom for symptom in self.symptoms_list 
            if query in symptom.lower()
        ]
        
        return suggestions[:limit]
    
    def get_all_symptoms(self) -> List[str]:
        """
        Get complete list of valid symptoms.
        
        Returns:
            Sorted list of all symptoms
        """
        return sorted(self.symptoms_list) if self.symptoms_list else []
    
    def get_recommended_doctor(self, disease_name: str) -> str:
        """Get recommended doctor specialist for a disease."""
        return self.DISEASE_TO_DOCTOR.get(disease_name, 'General Physician')
    
    def _generate_explanation(self, disease: str, symptoms: List[str]) -> str:
        """
        Generate neutral, detailed explanation for predicted disease.
        
        Avoids speculative language and focuses on detected symptoms.
        Includes category context and body location information.
        
        Args:
            disease: Predicted disease name
            symptoms: List of symptoms provided by user
        
        Returns:
            Human-readable, neutral explanation
        """
        if not symptoms:
            return f"Prediction for {disease} based on symptom analysis."
        
        # Find symptom-disease connections from our specific mapping
        explanations = []
        for symptom in symptoms[:3]:
            key = (disease, symptom)
            if key in self.SYMPTOM_DISEASE_EXPLANATIONS:
                explanations.append(self.SYMPTOM_DISEASE_EXPLANATIONS[key])
        
        # If we have specific symptom-disease explanations, use them
        if explanations:
            return ' '.join(explanations[:2]).capitalize()
        
        # Generate explanation based on symptom categories and disease properties
        symptom_str = ', '.join(symptoms[:3])
        
        # Check if it's a high-confidence category match
        if disease in ['Pneumonia', 'Bronchitis'] and 'fever' in symptoms and 'cough' in symptoms:
            return f"Respiratory infection indicated by symptoms: {symptom_str}. Fever and cough are classic indicators."
        
        if disease in ['Heart Attack'] and 'chest_pain' in symptoms:
            return f"⚠️ URGENT - Chest pain detected with other cardiac symptoms. Seek immediate medical attention. Symptoms: {symptom_str}."
        
        if disease in ['Diabetic'] and ('polyuria' in symptoms or 'polydipsia' in symptoms):
            return f"Metabolic condition indicated by increased urination and thirst. Symptoms: {symptom_str}."
        
        if disease in ['Migraine'] and 'severe_headache' in symptoms:
            return f"Neurological condition characterized by severe headache and associated symptoms: {symptom_str}."
        
        if disease in ['Arthritis', 'Rheumatoid Arthritis'] and 'joint_pain' in symptoms:
            return f"Joint-related condition indicated by joint pain and stiffness. Symptoms: {symptom_str}."
        
        # Default generic explanation
        if len(symptoms) >= 2:
            return f"Prediction based on detected symptoms: {symptom_str}."
        else:
            return f"Prediction for {disease} based on symptom pattern: {symptoms[0] if symptoms else 'unknown'}."
    
    def get_suggested_symptoms(self, partial_input: str = "", limit: int = 5) -> List[str]:
        """
        Get symptom suggestions for autocomplete/dropdown.
        
        Args:
            partial_input: Partial symptom text typed by user
            limit: Max suggestions to return
            
        Returns:
            List of suggested symptoms
        """
        if not partial_input:
            return self.symptoms_list[:limit]
        
        partial = partial_input.lower().strip()
        suggestions = []
        
        # Direct prefix matching
        for symptom in self.symptoms_list:
            if symptom.lower().startswith(partial):
                suggestions.append(symptom)
        
        # Partial matching if not enough results
        if len(suggestions) < limit:
            for symptom in self.symptoms_list:
                if partial in symptom.lower() and symptom not in suggestions:
                    suggestions.append(symptom)
        
        return suggestions[:limit]
    
    def get_recommended_doctor(self, disease_name: str) -> str:
        """
        Get recommended doctor specialist for a disease.
        
        Args:
            disease_name: Name of the disease
        
        Returns:
            Recommended doctor specialist name
        """
        return self.DISEASE_TO_DOCTOR.get(disease_name, 'General Physician')


# Singleton instance for convenience
_predictor_instance = None

def get_predictor(model_dir: str = None) -> AIPredictor:
    """
    Get or create a singleton AIPredictor instance.
    
    Args:
        model_dir: Directory containing model files (optional)
    
    Returns:
        AIPredictor instance
    """
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = AIPredictor(model_dir)
    return _predictor_instance
