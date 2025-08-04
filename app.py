from flask import Flask, render_template, request
from ce_model import predict

app = Flask(__name__)

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

@app.route('/predict', methods=['POST'])
def prediction():
    # Get form data
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
        form_data['agreement'],
        form_data['notice'],
        form_data['consumer'],
        form_data['matrimonial'],
        form_data['value']
    ]
    
    result, guidance = predict(data)
    return render_template("index.html", result=result, guidance=guidance, form_data=form_data)

if __name__ == '__main__':
    print("=" * 50)
    print("🏛️  LEGAL ASSISTANCE BOT STARTING...")
    print("=" * 50)
    print("📍 Server will be available at: http://127.0.0.1:5000")
    print("📍 Or visit: http://localhost:5000")
    print("🔧 Debug mode: ON")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
