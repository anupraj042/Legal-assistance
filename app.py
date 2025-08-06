from flask import Flask, render_template, request, jsonify, session
from candidate_elimination import load_cases, predict_legal_issue
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load CSV dataset at startup
dataset = load_cases("minimal_legal_cases.csv")

# Reset session
@app.route('/reset', methods=['GET'])
def reset():
    session.clear()
    return jsonify({"message": "Session reset."})

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chatbot')
def chatbot():
    return render_template('index.html')

@app.route('/legal-assistant')
def legal_assistant():
    return render_template('legal_form.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    step = session.get("step", 0)
    context = session.get("context", {})
    
    questions = [
        ("case_type", "What type of case is this? (Civil, Criminal, Family, Consumer, etc.)"),
        ("sub_type", "Can you specify the issue? (Eviction, Dowry, Divorce, etc.)"),
        ("value", "What is the value involved? (<10k, 10k-50k, >50k, N/A)"),
        ("agreement", "Did you sign any agreement? (Yes/No)"),
        ("notice", "Did you give a legal notice? (Yes/No)"),
        ("consumer", "Is this a consumer complaint? (Yes/No)"),
        ("matrimonial", "Is this related to a matrimonial issue? (Yes/No)")
    ]
    
    # If this is the first message or "start", begin the conversation
    if step == 0 and (user_input.lower() == "start" or user_input.lower() == "hello"):
        session["step"] = 1
        session["context"] = {}
        return jsonify({"reply": questions[0][1]})
    
    # If we're in the middle of questions
    if 1 <= step <= len(questions):
        # Store the answer for the current question
        current_key = questions[step - 1][0]
        context[current_key] = user_input
        session["context"] = context
        
        # Check if we have more questions
        if step < len(questions):
            session["step"] = step + 1
            next_question = questions[step][1]
            return jsonify({"reply": next_question})
        else:
            # All questions answered, make prediction
            prediction, guidance = predict_legal_issue(context, dataset)
            session.clear()
            return jsonify({
                "reply": f"✅ Legal Issue: {prediction}\n📘 Guidance: {guidance}\n\n📋 Case Summary:\n" + 
                        "\n".join([f"• {k.replace('_', ' ').title()}: {v}" for k, v in context.items()])
            })
    
    # If no step is set or invalid state, prompt to start
    return jsonify({"reply": "Hi! I'm your Legal Assistant. Type 'start' to begin analyzing your legal case."})

@app.route('/predict', methods=['POST'])
def predict():
    """Handle form-based prediction requests"""
    try:
        # Get JSON data from form
        if request.is_json:
            form_data = request.get_json()
        else:
            # Handle form data if needed
            form_data = request.form.to_dict()
        
        # Make prediction using the same function as chat
        prediction, guidance = predict_legal_issue(form_data, dataset)
        
        # Return JSON response for form
        return jsonify({
            "prediction": prediction,
            "confidence": "Medium",  # You can enhance this based on your algorithm
            "guidance": guidance,
            "case_summary": form_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)