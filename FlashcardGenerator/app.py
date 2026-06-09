from flask import Flask, render_template, request
from generator import extract_text_from_pdf, generate_flashcards
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    flashcards = []
    error = None

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        
        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)
            
            # Extract text and generate cards
            text = extract_text_from_pdf(file_path)
            if text.strip():
                flashcards = generate_flashcards(text)
                if not flashcards:
                    error = "Could not find clear definitions in this PDF. Try a textbook chapter."
            else:
                error = "Could not extract text from the PDF."
        else:
            error = "Please upload a valid PDF file."

    return render_template('index.html', flashcards=flashcards, error=error)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.mkdir('uploads')
    # Running on port 5002 so it doesn't conflict with your Chatbot or Summarizer
    app.run(debug=True, port=5002)