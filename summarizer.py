from transformers import pipeline

# We set the model to None initially so the server can boot instantly
_summarizer_model = None

def get_model():
    global _summarizer_model
    # Only load the model if it hasn't been loaded yet
    if _summarizer_model is None:
        print("Initializing DistilBART AI Engine... (This may take a minute on first run)")
        # We are using the distilled, faster version to save your RAM!
        _summarizer_model = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    return _summarizer_model

# Now it accepts BOTH text and summary_length to match your app.py!
def summarize_text(text, summary_length="medium"):
    try:
        if not text or len(text) < 50:
            return "Text is too short to summarize. Please provide a longer chapter."
            
        # Dynamically set the AI's generation length based on the UI input
        max_len = 150
        min_len = 40
        
        # Handle string-based lengths (short/medium/long)
        length_str = str(summary_length).lower()
        if length_str == "short":
            max_len = 60
            min_len = 20
        elif length_str == "long":
            max_len = 300
            min_len = 80
        # Handle integer-based lengths (if your UI uses a slider)
        elif length_str.isdigit():
            max_len = int(length_str)
            min_len = max(20, int(max_len * 0.3))

        # Failsafe: Don't let the AI try to generate a summary longer than the original text
        input_word_count = len(text.split())
        if max_len > input_word_count:
            max_len = max(20, int(input_word_count * 0.8))
            min_len = max(10, int(max_len * 0.3))

        # Call the lazy loader
        ai_engine = get_model()
        
        # Generate the summary with the dynamic lengths
        result = ai_engine(text, max_length=max_len, min_length=min_len, do_sample=False)
        return result[0]['summary_text']
        
    except Exception as e:
        return f"System Error during summarization: {str(e)}"
