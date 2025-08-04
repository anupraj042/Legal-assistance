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
def index():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def prediction():
    data = [
        request.form['case_type'],
        request.form['agreement'],
        request.form['notice'],
        request.form['consumer'],
        request.form['matrimonial'],
        request.form['value']
    ]
    result = predict(data)
    return render_template("index.html", result=result)

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
