import json
import wikipedia
import re
from difflib import get_close_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EduVerseChatbot:
    def __init__(self):
        # Load knowledge base from JSON
        try:
            with open('knowledge_base.json', 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
        except FileNotFoundError:
            self.knowledge_base = []
            print("Warning: knowledge_base.json not found. Using Wikipedia only.")
        
        # Add basic conversational skills
        self.greetings = ["hi", "hello", "hey", "good morning", "good evening", "what's up", "help"]
        self.greeting_response = "Hello! I am your Edu Verse Assistant. I can answer your study questions, define technical terms, or pull summaries from Wikipedia. How can I help you today?"

        # Initialize TF-IDF Vectorizer
        if self.knowledge_base:
            self.questions = [item["question"].lower() for item in self.knowledge_base]
            self.vectorizer = TfidfVectorizer()
            # Pre-calculate the TF-IDF matrix for all KB questions
            self.kb_vectors = self.vectorizer.fit_transform(self.questions)

    def search_local_tfidf(self, user_input):
        """Search knowledge base using Typo Correction + TF-IDF Cosine Similarity"""
        if not self.knowledge_base:
            return None
            
        # --- LAYER 1: TYPO CORRECTION (Fuzzy Pre-Filter) ---
        user_input_lower = user_input.lower().strip()
        
        # Use fuzzy matching to correct the typo first
        corrections = get_close_matches(user_input_lower, self.questions, n=1, cutoff=0.6)
        search_term = corrections[0] if corrections else user_input_lower

        # --- LAYER 2: SEMANTIC MATCHING (TF-IDF) ---
        user_vector = self.vectorizer.transform([search_term])
        similarities = cosine_similarity(user_vector, self.kb_vectors)[0]
        
        # Get the index of the highest similarity score
        best_match_idx = similarities.argmax()
        best_score = similarities[best_match_idx]
        
        # Threshold for accepting the answer
        if best_score > 0.3:
            return self.knowledge_base[best_match_idx]["answer"]
            
        return None

    def clean_wiki_query(self, user_input):
        """Strip common question phrases so Wikipedia can find the actual noun"""
        query = user_input.lower()
        prefixes = ["what is a ", "what is an ", "what is ", "what are ", "who is ", "tell me about ", "define ", "explain "]
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query.replace(prefix, "", 1)
                break
        return re.sub(r'[^\w\s]', '', query).strip()

    def get_response(self, user_input):
        user_input_lower = user_input.lower().strip()

        # Step 1: Check for basic greetings
        if user_input_lower in self.greetings:
            return self.greeting_response

        # Step 2: Try local Q/A with TF-IDF Semantic Match
        local_answer = self.search_local_tfidf(user_input)
        if local_answer:
            return local_answer  

        # Step 3: Wikipedia fallback
        cleaned_query = self.clean_wiki_query(user_input_lower)
        if not cleaned_query:
            return "I didn't quite catch that. Could you rephrase your question?"

        try:
            summary = wikipedia.summary(cleaned_query, sentences=2, auto_suggest=True)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:2] if len(e.options) >= 2 else e.options
            return f"That could mean a few things. Did you mean {options[0]} or {options[1]}?"
        except wikipedia.exceptions.PageError:
            return f"I couldn't find specific information on '{cleaned_query}'. Could you check your spelling?"
        except Exception:
            return "Sorry, I am having trouble connecting to my database right now."