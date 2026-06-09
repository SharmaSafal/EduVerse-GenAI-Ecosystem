import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def generate_flashcards(text, max_cards=50):
    # Clean up PDF text formatting
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    flashcards = {}
    
    # Use enumerate so we can look backward at the previous sentence
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if len(sentence) > 250 or len(sentence) < 20: 
            continue

        term = None

        # Pattern 1: Term is at the END
        post_keywords = [" is known as ", " is called ", " are called ", " refers to as "]
        for kw in post_keywords:
            if kw in sentence.lower():
                parts = re.split(kw, sentence, flags=re.IGNORECASE)
                term_raw = parts[-1].strip().strip('."\',')
                if 0 < len(term_raw.split()) <= 3:
                    term = term_raw.title()
                break

        # Pattern 2: Term is at the START
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

        # Save the card and handle Coreference Resolution (Missing Context)
        if term and term not in flashcards:
            definition = sentence
            
            # If the sentence starts with a pointer word, grab the previous sentence
            referential_starts = ["this", "such", "it", "these"]
            first_word = sentence.split()[0].lower() if sentence else ""
            
            if first_word in referential_starts and i > 0:
                prev_sentence = sentences[i-1].strip()
                # Ensure the previous sentence isn't massive before gluing them
                if 20 < len(prev_sentence) < 250:
                    definition = prev_sentence + " " + sentence

            flashcards[term] = definition

    final_cards = [{"term": k, "definition": v} for k, v in list(flashcards.items())[:max_cards]]
    return final_cards