from flask import Blueprint, request, jsonify, render_template, session, redirect, flash
from ai_engine import AIPredictor
from backend.models.prediction_history_model import save_prediction_history, get_user_prediction_history
from backend.models.prediction_history_model import get_prediction_analytics
from backend.utils.auth import login_required
import json

ml_bp = Blueprint('ml', __name__)

# Initialize the AI Predictor
try:
    predictor = AIPredictor()
except Exception as e:
    print(f"Warning: Failed to initialize AIPredictor: {e}")
    predictor = None


# Wrapper functions for backward compatibility
def predict_disease_dl(user_symptoms):
    """
    Backward compatible wrapper for disease prediction.
    Converts list of symptoms to structured prediction format.
    """
    if not predictor:
        return None
    
    try:
        # Accept both comma-separated string and list
        if isinstance(user_symptoms, str):
            natural_input = user_symptoms
        else:
            natural_input = ', '.join(user_symptoms)
        
        # Get prediction from new predictor
        result = predictor.predict(natural_input)
        
        # Convert to old format for compatibility
        if result and result.get('predictions'):
            top_prediction = result['predictions'][0]
            return {
                'input_symptoms': result.get('symptoms', []),
                'disease': top_prediction.get('disease', 'Unknown'),
                'confidence': top_prediction.get('confidence', 0),
                'severity': result.get('severity', 'Unknown'),
                'recommended_doctor': predictor.get_recommended_doctor(
                    top_prediction.get('disease', 'Unknown')
                ),
                'precautions': 'Consult a healthcare professional for proper diagnosis and treatment.'
            }
        return None
    except Exception as e:
        print(f"Prediction error: {e}")
        return None


def get_symptom_suggestions(query, limit=10):
    """Get symptom suggestions based on query."""
    if not predictor:
        return []
    return predictor.get_symptom_suggestions(query, limit)


def get_all_symptoms():
    """Get all available symptoms."""
    if not predictor:
        return []
    return predictor.get_all_symptoms()


@ml_bp.route('/api/symptom-suggestions')
def symptom_suggestions():
    """API endpoint for symptom auto-suggestions"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 10))
    
    if not predictor:
        return jsonify({'suggestions': []})
    
    suggestions = predictor.get_suggested_symptoms(query, limit)
    return jsonify({'suggestions': suggestions})


@ml_bp.route('/api/all-symptoms')
def api_all_symptoms():
    """API endpoint for getting all symptoms"""
    if not predictor:
        return jsonify({'symptoms': []})
    
    symptoms = predictor.get_all_symptoms()
    return jsonify({'symptoms': symptoms})

@ml_bp.route('/ml-predict', methods=['GET', 'POST'])
@login_required
def ml_predict():
    """Disease prediction page with advanced AI features"""
    if request.method == 'POST':
        try:
            symptoms_input = request.form.get('symptoms', '').strip()

            if not symptoms_input:
                flash('Please enter at least one symptom', 'error')
                return redirect('/ml-predict')

            # Get prediction using new AIPredictor
            if not predictor:
                flash('Prediction service unavailable. Please try again later.', 'error')
                return redirect('/ml-predict')
            
            result = predictor.predict(symptoms_input)
            
            # Debug logging
            print(f"DEBUG: Prediction result: {result}")
            
            # Validate input FIRST
            if not result['input_validation']['valid']:
                error_msg = result['input_validation']['message']
                print(f"DEBUG: Validation failed: {error_msg}")
                flash(f"Invalid input: {error_msg}", 'error')
                return redirect('/ml-predict')
            
            # Check if predictions exist
            if not result or not result.get('predictions'):
                error_msg = result.get('error', 'No predictions generated')
                print(f"DEBUG: No predictions: {error_msg}")
                flash(f'Prediction failed: {error_msg}', 'error')
                return redirect('/ml-predict')
            
            # Format for history and display
            top_prediction = result['predictions'][0]
            history_record = {
                'input_symptoms': result.get('symptoms', []),
                'disease': top_prediction.get('disease', 'Unknown'),
                'confidence': top_prediction.get('confidence', 0),
                'severity': result.get('severity', 'Unknown'),
                'recommended_doctor': top_prediction.get('doctor', 'General Physician'),
                'precautions': 'Consult a healthcare professional for proper diagnosis and treatment.'
            }
            
            # Save to history
            user_id = session.get('user_id')
            if user_id:
                save_prediction_history(user_id, history_record)

            # Build response with top 3 predictions including explanations
            predictions_display = []
            for pred in result['predictions'][:3]:
                predictions_display.append({
                    'disease': pred['disease'],
                    'confidence': f"{pred['confidence']:.1f}%",
                    'confidence_value': pred['confidence'],  # For progress bar
                    'doctor': pred.get('doctor', 'General Physician'),
                    'explanation': pred.get('explanation', 'Based on the symptoms provided.')
                })

            # Build chat-style context for a response
            symptoms_str = ', '.join(result['symptoms']) if result['symptoms'] else 'your symptoms'
            explanation = top_prediction.get('explanation', 'Analyzing your symptoms...')
            
            chat_history = [
                {'role': 'user', 'text': symptoms_input},
                {
                    'role': 'assistant',
                    'text': f"Based on {symptoms_str}, the top prediction is: <strong>{top_prediction['disease']}</strong> ({top_prediction['confidence']:.1f}% confidence). {explanation}. Recommended specialist: <strong>{top_prediction.get('doctor', 'General Physician')}</strong>. Severity: <strong>{result['severity']}</strong>."
                }
            ]

            return render_template('predict.html',
                                 prediction=history_record,
                                 predictions_list=predictions_display,
                                 symptoms_input=symptoms_input,
                                 chat_history=chat_history,
                                 severity=result['severity'],
                                 severity_color='danger' if result['severity'] == 'High' else 'warning' if result['severity'] == 'Medium' else 'success')

        except Exception as e:
            print(f"Prediction error: {e}")
            flash('An error occurred during prediction', 'error')
            return redirect('/ml-predict')

    return render_template('predict.html')

@ml_bp.route('/prediction-history')
@login_required
def prediction_history():
    """View prediction history"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    history = get_user_prediction_history(user_id)
    return render_template('prediction_history.html', history=history)

@ml_bp.route('/api/all-symptoms')
def all_symptoms_list():
    """Get all available symptoms"""
    if not predictor:
        return jsonify({'symptoms': []})
    symptoms = predictor.get_all_symptoms()
    return jsonify({'symptoms': symptoms})

@ml_bp.route('/api/prediction-analytics')
@login_required
def prediction_analytics():
    """Get prediction analytics for dashboard"""
    # Only allow admin access
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    analytics = get_prediction_analytics()
    return jsonify(analytics)