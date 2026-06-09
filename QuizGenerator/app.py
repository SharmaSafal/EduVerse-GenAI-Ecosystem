from flask import Flask, render_template, request
from quiz_engine import extract_text_from_pdf, generate_quiz
from werkzeug.utils import secure_filename
import os
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    quiz_data = []
    error = None

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        
        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            # Professional security practice for file names
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            
            try:
                # YOUR ORIGINAL LOGIC
                text = extract_text_from_pdf(file_path)
                if text.strip():
                    quiz_data = generate_quiz(text)
                    if not quiz_data:
                        error = "Not enough clear definitions found to create a multiple-choice quiz. Try a denser textbook chapter."
                else:
                    error = "Could not extract text from the PDF."
            except Exception as e:
                error = f"System Error during extraction: {str(e)}"
        else:
            error = "Please upload a valid PDF file."

    # CRITICAL UI BRIDGE: Passing your 'quiz_data' as 'questions' so the new UI can read it
    return render_template('index.html', questions=quiz_data, error=error)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    # This catches the UI form submission when the user finishes the quiz.
    # For now, it returns a random high score to trigger the Green Score Dashboard.
    # (You can easily wire this up to compare request.form answers to your AI's answer key later!)
    mock_scores = ["100%", "85%", "92%"]
    final_score = random.choice(mock_scores)
    
    return render_template('index.html', score=final_score)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        
    # CRITICAL: use_reloader=False prevents RAM crashes when launching via master script
    app.run(debug=True, use_reloader=False, port=5003)