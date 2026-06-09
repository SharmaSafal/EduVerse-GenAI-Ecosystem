import fitz  # PyMuPDF
import re
import random

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def generate_quiz(text, max_questions=10):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    extracted_data = {}
    
    # Stable extraction logic (Same as Flashcards MVP)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 250 or len(sentence) < 30: 
            continue

        term = None

        # Pattern 1: Term at END
        post_keywords = [" is known as ", " is called ", " are called ", " refers to as "]
        for kw in post_keywords:
            if kw in sentence.lower():
                parts = re.split(kw, sentence, flags=re.IGNORECASE)
                term_raw = parts[-1].strip().strip('."\',')
                if 0 < len(term_raw.split()) <= 3:
                    term = term_raw.title()
                break

        # Pattern 2: Term at START
        if not term:
            pre_keywords = [" is defined as ", " refers to ", " stands for "]
            for kw in pre_keywords:
                if kw in sentence.lower():
                    parts = re.split(kw, sentence, flags=re.IGNORECASE)
                    term_raw = parts[0].strip()
                    term_raw = re.sub(r'^(The|A|An|Generally,|In this case,|Such a)\s+', '', term_raw, flags=re.IGNORECASE)
                    if 0 < len(term_raw.split()) <= 3:
                        term = term_raw.title()
                    break

        if term and term not in extracted_data:
            extracted_data[term] = sentence

    # Convert to Quiz Format
    all_terms = list(extracted_data.keys())
    quiz_questions = []

    # Only build the quiz if we have enough terms for multiple choice
    if len(all_terms) >= 4:
        # Shuffle the terms to get random questions
        random.shuffle(all_terms)
        
        for term in all_terms[:max_questions]:
            question_text = extracted_data[term]
            
            # Mask the term in the question so it doesn't give away the answer
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            masked_question = pattern.sub("______", question_text)

            # Get 3 random wrong options
            wrong_options = random.sample([t for t in all_terms if t != term], 3)
            
            # Combine correct and wrong options, then shuffle them
            options = wrong_options + [term]
            random.shuffle(options)

            quiz_questions.append({
                "question": masked_question,
                "options": options,
                "answer": term
            })

    return quiz_questions