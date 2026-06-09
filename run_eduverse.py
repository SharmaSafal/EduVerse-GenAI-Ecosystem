import subprocess
import sys
import time
import os
import json
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_eduverse_key' # Required for login sessions

# --- AUTHENTICATION LOGIC ---
def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        
        if username in users and users[username]['password'] == password:
            session['user'] = username
            session['details'] = users[username]
            return redirect(url_for('portal'))
        else:
            return render_template('login.html', error="Invalid credentials")
            
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('details', None)
    return redirect(url_for('login'))

# --- PORTAL LOGIC ---
@app.route('/')
def portal():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('portal.html', user=session['details'])

@app.route('/welcome')
def welcome():
    # The Billion-Dollar Command Center Dashboard
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
            body {
                margin: 0; padding: 0; font-family: 'Inter', sans-serif;
                background-color: transparent; 
                color: #f8fafc; display: flex; flex-direction: column; 
                align-items: center; justify-content: center; height: 80vh;
            }
            .hero { text-align: center; margin-bottom: 50px; animation: fadeIn 1s ease-out; }
            .hero h1 {
                font-size: 72px; margin: 0 0 15px 0; font-weight: 800;
                background: linear-gradient(270deg, #3b82f6, #8b5cf6, #ec4899, #3b82f6);
                background-size: 800% 800%;
                -webkit-background-clip: text; background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: gradientFlow 8s ease infinite;
            }
            .hero p { color: #94a3b8; font-size: 20px; font-weight: 400; letter-spacing: 1px; }
            
            .grid { display: flex; gap: 25px; animation: slideUp 1s ease-out 0.3s backwards; flex-wrap: wrap; justify-content: center; }
            .card {
                background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px 30px; border-radius: 16px; 
                text-align: center; width: 220px; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
                transition: all 0.3s ease; position: relative; overflow: hidden;
            }
            .card::before {
                content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
                background: linear-gradient(to right, transparent, rgba(255,255,255,0.05), transparent);
                transform: skewX(-20deg); transition: 0.5s;
            }
            .card:hover::before { left: 150%; }
            .card:hover { transform: translateY(-5px); border-color: rgba(59, 130, 246, 0.4); background: rgba(30, 41, 59, 0.7); }
            
            .card-icon { font-size: 32px; margin-bottom: 15px; }
            .card h3 { margin: 0 0 10px 0; color: #f8fafc; font-size: 18px; }
            .status { color: #64748b; font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 8px; }
            .status-dot { width: 10px; height: 10px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 12px #22c55e; animation: pulse 2s infinite; }
            .status-dot.lazy { background: #f59e0b; box-shadow: 0 0 12px #f59e0b; }
            
            @keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
            @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
            @keyframes gradientFlow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>EduVerse Hub</h1>
            <p>Neural pathways synchronized. Select a module to begin.</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-icon">🧠</div>
                <h3>AI Chat Engine</h3>
                <div class="status"><span class="status-dot"></span> Live Vector Search</div>
            </div>
            <div class="card">
                <div class="card-icon">📄</div>
                <h3>NLP Summarizer</h3>
                <div class="status"><span class="status-dot lazy"></span> Lazy-Loaded</div>
            </div>
            <div class="card">
                <div class="card-icon">⚡</div>
                <h3>Flashcards</h3>
                <div class="status"><span class="status-dot"></span> Memory Synced</div>
            </div>
            <div class="card">
                <div class="card-icon">🎯</div>
                <h3>Quiz Node</h3>
                <div class="status"><span class="status-dot"></span> Engine Ready</div>
            </div>
        </div>
    </body>
    </html>
    """

# --- LAUNCHER LOGIC ---
if __name__ == '__main__':
    print("🚀 Booting up EduVerse Enterprise Environment...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    modules = ["StudentChatbot", "TextSummarizer", "FlashcardGenerator", "QuizGenerator", "StudyPlanner"]
    processes = []
    
    # ---------------------------------------------------------
    # THE STEALTH FIX: Runs all apps invisibly in the background
    # ---------------------------------------------------------
    CREATE_NO_WINDOW = 0x08000000 
    
    for module in modules:
        module_path = os.path.join(base_dir, module)
        try:
            print(f"Starting {module} in stealth mode...")
            p = subprocess.Popen([sys.executable, "app.py"], cwd=module_path, creationflags=CREATE_NO_WINDOW)
            processes.append(p)
            time.sleep(1) 
        except Exception as e:
            print(f"❌ Skipped {module}: {str(e)}")
            
    print("✅ System Ready! Go to: http://127.0.0.1:8000")
    try:
        app.run(debug=False, port=8000) 
    finally:
        print("Shutting down all background processes...")
        for p in processes:
            p.terminate()