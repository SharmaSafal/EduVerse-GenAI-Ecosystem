from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import math
import os

app = Flask(__name__)

# ---------------------------------------------------------
# 🧠 SIMULATED AI KNOWLEDGE GRAPH
# ---------------------------------------------------------
KNOWLEDGE_BASE = {
    "python": {
        "Beginner": ["Variables & Data Types", "Control Flow (If/Else, Loops)", "Functions & Scope"],
        "Intermediate": ["Data Structures (Lists, Dicts, Sets)", "OOPs Concepts", "File Handling & Exceptions"],
        "Advanced": ["Decorators & Generators", "Multithreading/Asyncio", "API Integration"]
    },
    "dsa": {
        "Beginner": ["Arrays & Strings", "Time & Space Complexity", "Basic Recursion"],
        "Intermediate": ["Linked Lists", "Stacks & Queues", "Trees & BST", "Sorting Algorithms"],
        "Advanced": ["Graphs (BFS/DFS)", "Dynamic Programming", "Trie & Advanced Structures"]
    },
    "math": {
        "Beginner": ["Algebraic Expressions", "Basic Trigonometry", "Functions & Graphs"],
        "Intermediate": ["Differential Calculus", "Integral Calculus", "Matrix Operations"],
        "Advanced": ["Differential Equations", "Vector Spaces", "Probability Distributions"]
    }
}

def analyze_subject(subject_name):
    subject_key = subject_name.lower().strip()
    
    # Check if we have a pre-mapped syllabus
    for key in KNOWLEDGE_BASE:
        if key in subject_key:
            return KNOWLEDGE_BASE[key]
            
    # Fallback for unknown subjects: generic progressive structure
    return {
        "Beginner": ["Core Fundamentals", "Basic Terminology", "Introductory Concepts"],
        "Intermediate": ["Applied Mechanisms", "System Architecture", "Standard Problem Solving"],
        "Advanced": ["Edge Cases", "Complex Implementations", "Optimization & Theory"]
    }

def get_study_strategy(subject_name):
    subject_key = subject_name.lower()
    if "math" in subject_key or "physics" in subject_key:
        return "Solve 10-15 numerical problems. Focus on formula derivation."
    elif "dsa" in subject_key or "algorithm" in subject_key:
        return "Code from scratch. Solve 3 LeetCode/HackerRank problems."
    elif "python" in subject_key or "java" in subject_key or "programming" in subject_key:
        return "Write functional code. Build a micro-script to test the concept."
    else:
        return "Use Feynman Technique: Read, summarize, and explain it out loud."

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_topics', methods=['POST'])
def get_topics():
    data = request.json
    subject = data.get('subject', '')
    
    # 1. Map the syllabus intelligently
    syllabus = analyze_subject(subject)
    return jsonify({"status": "success", "syllabus": syllabus})

@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    data = request.json
    subject = data.get('subject')
    exam_date_str = data.get('exam_date')
    selected_topics = data.get('topics') # Expecting a list of dicts: [{'name': '...', 'level': 'Beginner'}]
    
    # Calculate Days Left
    exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
    today = datetime.now()
    days_left = (exam_date - today).days

    if days_left <= 0:
        return jsonify({"error": "Exam date must be in the future."})

    # Sort topics by logical progression (Beginner -> Int -> Adv)
    level_order = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    selected_topics.sort(key=lambda x: level_order.get(x['level'], 4))

    strategy = get_study_strategy(subject)
    schedule = []
    
    # Distribute topics intelligently across the available days
    # Reserve the last 10% of days for Mock Tests and Review
    review_days = max(1, math.floor(days_left * 0.15))
    learning_days = days_left - review_days
    
    topics_per_day = math.ceil(len(selected_topics) / learning_days) if learning_days > 0 else len(selected_topics)
    
    topic_index = 0
    for day in range(1, days_left + 1):
        current_date = today + timedelta(days=day)
        date_str = current_date.strftime("%b %d, %Y")
        
        day_plan = {
            "day_num": day,
            "date": date_str,
            "tasks": [],
            "is_review": False
        }
        
        # If it's a learning day and we still have topics left
        if day <= learning_days and topic_index < len(selected_topics):
            daily_topics = []
            for _ in range(topics_per_day):
                if topic_index < len(selected_topics):
                    daily_topics.append(selected_topics[topic_index])
                    topic_index += 1
            
            for t in daily_topics:
                day_plan["tasks"].append({
                    "type": "LEARN",
                    "level": t['level'],
                    "topic": t['name'],
                    "strategy": strategy,
                    "time": "2 Hours"
                })
        
        # If it's a review day or we ran out of topics
        else:
            day_plan["is_review"] = True
            day_plan["tasks"].append({
                "type": "MOCK TEST",
                "level": "Review",
                "topic": "Full Syllabus Synthetic Assessment",
                "strategy": "Simulate exam conditions. Identify weak points.",
                "time": "3 Hours"
            })
            
        schedule.append(day_plan)

    return jsonify({
        "status": "success", 
        "days_left": days_left,
        "schedule": schedule
    })

if __name__ == '__main__':
    # Port 5004 for the Planner Engine
    app.run(debug=True, use_reloader=False, port=5004)