from flask import Flask, render_template, request
from summarizer import summarize_text  # Import your summarizer function
from werkzeug.utils import secure_filename # Professional best practice for file uploads
import fitz  # PyMuPDF
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = ''
    if request.method == 'POST':
        input_text = request.form.get('input_text', '')
        summary_length = request.form.get('length', 'medium')

        # File upload logic
        uploaded_file = request.files.get('file')
        if uploaded_file and uploaded_file.filename != '':
            # Secure the filename before saving it
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            try:
                if filename.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        input_text = f.read()
                elif filename.endswith('.pdf'):
                    with fitz.open(file_path) as pdf:
                        input_text = ""
                        for page in pdf:
                            input_text += page.get_text()
            except Exception as e:
                summary = f"Error reading file: {str(e)}"
                return render_template('index.html', summary=summary)

        # Validate input
        if len(input_text.strip()) == 0:
            summary = "No valid text found. Please enter or upload something."
        elif len(input_text) > 3000:
            summary = "Input too long! Please reduce it to under 3000 characters."
        else:
            summary = summarize_text(input_text, summary_length)

    return render_template('index.html', summary=summary)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads') # Using makedirs is safer
        
    # ---------------------------------------------------------
    # CRITICAL ARCHITECTURE FIXES:
    # 1. use_reloader=False prevents RAM spikes/crashes with Transformers
    # 2. port=5001 prevents port collisions with the Chatbot (5000)
    # ---------------------------------------------------------
    app.run(debug=True, use_reloader=False, port=5001)