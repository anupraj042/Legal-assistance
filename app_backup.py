from flask import Flask, render_template, request, jsonify, session
from candidate_elimination import predict, train_model, get_model_info
import uuid

app = Flask(__name__)
app.secret_key = 'legal_assistant_secret_key_2024'  # Change this in production

@app.after_request
def after_request(response):
    # Add security headers
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/legal-assistant')
def index():
    return render_template("index.html")

@app.route('/model-info')
def model_info():
    """Display information about the trained Candidate Elimination model"""
    info = get_model_info()
    return f"<pre>{info}</pre>"

@app.route('/test_button.html')
def test_button():
    """Test page for button functionality"""
    with open('test_button.html', 'r') as f:
        return f.read()

@app.route('/chatbot')
def chatbot():
    """Render the conversational chatbot interface"""
    return render_template("chatbot_working.html")

@app.route('/chatbot-simple')
def chatbot_simple():
    """Render the simple chatbot interface for debugging"""
    return render_template("chatbot_simple.html")

@app.route('/chatbot-working')
def chatbot_working():
    """Render the fully working chatbot interface"""
    return render_template("chatbot_working.html")

@app.route('/chat/start', methods=['POST'])
def start_chat():
    """Initialize a new chat session"""
    session_id = str(uuid.uuid4())
    session['chat_id'] = session_id
    session['chat_data'] = {}
    session['current_question'] = 0
    
    # Define the conversation flow
    questions = [
        {
            "id": "case_type",
            "question": "What type of legal case do you have?",
            "type": "dropdown",
            "options": ["Civil", "Criminal", "Consumer", "Family", "Environmental", "PIL"]
        },
        {
            "id": "sub_type",
            "question": "What is the specific sub-type of your case?",
            "type": "dropdown",
            "options": ["Property Dispute", "Theft", "Non-Delivery", "Divorce", "Pollution", "RTI Delay", 
                       "Cheque Bounce", "Domestic Violence", "False Ads", "Maintenance", "Illegal Mining",
                       "Eviction", "Dowry Harassment", "Child Custody", "Land Violation"]
        },
        {
            "id": "value",
            "question": "What is the monetary value involved in your case?",
            "type": "dropdown",
            "options": ["<10k", "10k-50k", ">50k"]
        },
        {
            "id": "agreement",
            "question": "Was there any agreement or contract signed?",
            "type": "yesno"
        },
        {
            "id": "notice",
            "question": "Was any legal notice given to the other party?",
            "type": "yesno"
        },
        {
            "id": "consumer",
            "question": "Is this related to a consumer complaint?",
            "type": "yesno"
        },
        {
            "id": "matrimonial",
            "question": "Is this a matrimonial (marriage-related) issue?",
            "type": "yesno"
        }
    ]
    
    session['questions'] = questions
    
    return jsonify({
        "message": "Hello! I'm your Legal Assistant Bot. I'll ask you a few questions to understand your case better.",
        "question": questions[0]["question"],
        "question_type": questions[0]["type"],
        "options": questions[0].get("options", []),
        "question_id": questions[0]["id"]
    })

@app.route('/chat/answer', methods=['POST'])
def process_answer():
    """Process user's answer and return next question or final result"""
    data = request.get_json()
    answer = data.get('answer')
    question_id = data.get('question_id')
    
    # Store the answer
    if 'chat_data' not in session:
        session['chat_data'] = {}
    
    session['chat_data'][question_id] = answer
    session['current_question'] = session.get('current_question', 0) + 1
    
    questions = session.get('questions', [])
    current_q_index = session.get('current_question', 0)
    
    # Check if we have more questions
    if current_q_index < len(questions):
        next_question = questions[current_q_index]
        return jsonify({
            "message": f"Got it! {answer}",
            "question": next_question["question"],
            "question_type": next_question["type"],
            "options": next_question.get("options", []),
            "question_id": next_question["id"]
        })
    else:
        # All questions answered, make prediction
        chat_data = session.get('chat_data', {})
        
        # Convert chat data to prediction format
        # Map the value ranges to match the training data format
        value_mapping = {
            "<10k": "<10k",
            "10k-50k": "10k-50k", 
            ">50k": ">50k"
        }
        
        case_data = [
            chat_data.get('case_type', ''),
            chat_data.get('sub_type', ''),
            value_mapping.get(chat_data.get('value', ''), chat_data.get('value', '')),
            chat_data.get('agreement', ''),
            chat_data.get('notice', ''),
            chat_data.get('consumer', ''),
            chat_data.get('matrimonial', '')
        ]
        
        # Make prediction
        result, guidance = predict(case_data)
        
        # Generate case summary
        case_summary = {
            "Case Type": chat_data.get('case_type', 'Not specified'),
            "Sub-Type": chat_data.get('sub_type', 'Not specified'),
            "Value Involved": chat_data.get('value', 'Not specified'),
            "Agreement Signed": chat_data.get('agreement', 'Not specified'),
            "Notice Given": chat_data.get('notice', 'Not specified'),
            "Consumer Complaint": chat_data.get('consumer', 'Not specified'),
            "Matrimonial Issue": chat_data.get('matrimonial', 'Not specified')
        }
        
        return jsonify({
            "final_result": True,
            "prediction": result,
            "guidance": guidance,
            "case_summary": case_summary,
            "message": "Thank you for providing all the information! Here's my analysis of your case:"
        })

@app.route('/chat/reset', methods=['POST'])
def reset_chat():
    """Reset the chat session"""
    session.clear()
    return jsonify({"message": "Chat session reset. You can start a new conversation."})

@app.route('/predict', methods=['POST'])
def prediction():
    # Handle both JSON and form data
    if request.is_json:
        # JSON data from chatbot
        json_data = request.get_json()
        form_data = {
            'case_type': json_data.get('case_type', ''),
            'sub_type': json_data.get('sub_type', ''),
            'agreement': json_data.get('agreement', ''),
            'notice': json_data.get('notice', ''),
            'consumer': json_data.get('consumer', ''),
            'matrimonial': json_data.get('matrimonial', ''),
            'value': json_data.get('value', '')
        }
        
        # Map the value ranges to match the training data format
        value_mapping = {
            "<10k": "<10k",
            "10k-50k": "10k-50k", 
            ">50k": ">50k"
        }
        
        case_data = [
            form_data.get('case_type', ''),
            form_data.get('sub_type', ''),
            value_mapping.get(form_data.get('value', ''), form_data.get('value', '')),
            form_data.get('agreement', ''),
            form_data.get('notice', ''),
            form_data.get('consumer', ''),
            form_data.get('matrimonial', '')
        ]
        
        result, guidance = predict(case_data)
        
        # Return JSON response for chatbot
        return jsonify({
            "prediction": result,
            "confidence": "Medium",  # You can enhance this based on your algorithm
            "guidance": guidance,
            "case_summary": form_data
        })
    else:
        # Form data from traditional form
        form_data = {
            'case_type': request.form['case_type'],
            'sub_type': request.form['sub_type'],
            'agreement': request.form['agreement'],
            'notice': request.form['notice'],
            'consumer': request.form['consumer'],
            'matrimonial': request.form['matrimonial'],
            'value': request.form['value']
        }
        
        data = [
            form_data['case_type'],
            form_data['sub_type'],
            form_data['value'],
            form_data['agreement'],
            form_data['notice'],
            form_data['consumer'],
            form_data['matrimonial']
        ]
        
        result, guidance = predict(data)
        return render_template("index.html", result=result, guidance=guidance, form_data=form_data)

if __name__ == '__main__':
    print("=" * 50)
    print("🏛️  LEGAL ASSISTANCE BOT STARTING...")
    print("=" * 50)
    
    # Train the Candidate Elimination model
    print("🎯 Training Candidate Elimination Algorithm...")
    if train_model():
        print("✅ Model training completed successfully!")
    else:
        print("❌ Model training failed!")
    
    print("=" * 50)
    print("📍 Server will be available at: http://127.0.0.1:5000")
    print("📍 Or visit: http://localhost:5000")
    print("📍 Model info available at: http://localhost:5000/model-info")
    print("🔧 Debug mode: ON")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
