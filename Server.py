import sqlite3
import google.generativeai as genai
from flask import Flask, request, redirect, url_for, render_template, jsonify, session
import matplotlib.pyplot as plt
import numpy as np
import os
import pyttsx3
import threading

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"  # Required for session management

# SQLite Database Files
USER_DB = "GrandDataBase.sql"
QUERY_DB = "QueryDataBase.sql"

# Initialize Databases
def init_db():
    with sqlite3.connect(USER_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            tag TEXT NOT NULL)''')
        conn.commit()

    with sqlite3.connect(QUERY_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS queries (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,  -- Patient's Username
                            query TEXT NOT NULL,
                            ai_response TEXT NOT NULL,
                            verification TEXT DEFAULT "",
                            cli_username TEXT DEFAULT "",  -- Clinician's Username
                            status TEXT DEFAULT "Not Verified")''')
        conn.commit()

init_db()  # Run initialization on startup

# Configure AI Model
genai.configure(api_key="AIzaSyBilD2uRwotu_MuUhkW1N1VfyqZfLpad4o")
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to generate AI response
def generate_ai_response(query):
    response = model.generate_content(query)
    return response.text  # Extract AI response text

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        tag = request.form.get('tag')

        with sqlite3.connect(USER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                return "Username already exists. Try a different one!", 400

            cursor.execute("INSERT INTO users (username, password, tag) VALUES (?, ?, ?)", (username, password, tag))
            conn.commit()

        return redirect(url_for('login'))

    return render_template("signup.html")

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with sqlite3.connect(USER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tag FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()

        if not user:
            return "Invalid username or password", 401

        session['username'] = username  # Store the logged-in user

        tag = user[0]
        if tag == "C":
            return redirect(url_for('clinician_home'))
        elif tag == "P":
            return redirect(url_for('patient_home'))
        elif tag == "H":
            return redirect(url_for('hospital_home'))

    return render_template("login.html")

# Fetch Previous Chats (Only for the logged-in user)
def get_previous_chats(username):
    with sqlite3.connect(QUERY_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, query FROM queries WHERE username=? ORDER BY id DESC", (username,))
        return cursor.fetchall()

# Home Page (Patient Chat) - Show Only User's Chats
@app.route('/patient_home')
def patient_home():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    username = session['username']
    previous_chats = get_previous_chats(username)
    return render_template("patient_home.html", previous_chats=previous_chats)

# Get Full Chat History (Including Verification Status)
@app.route('/get_chat/<int:chat_id>')
def get_chat(chat_id):
    with sqlite3.connect(QUERY_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT query, ai_response, status, verification FROM queries WHERE id=?", (chat_id,))
        chat = cursor.fetchone()
    
    return jsonify({
        "query": chat[0], 
        "response": chat[1], 
        "status": chat[2], 
        "verification": chat[3] if chat[3] else None  # Send verification only if available
    })

# Clinician Home Page - View and Verify Queries
@app.route('/clinician_home')
def clinician_home():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    username = session['username']
    with sqlite3.connect(QUERY_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, query, ai_response, verification, cli_username, status FROM queries")
        queries = [{"id": row[0], "username": row[1], "query": row[2], "ai_response": row[3], "verification": row[4], "cli_username": row[5], "status": row[6]} for row in cursor.fetchall()]

    return render_template("clinician_home.html", queries=queries, clinician_username=username)

# Clinician Verification - Update AI Response Status
@app.route('/verify_response', methods=['POST'])
def verify_response():
    if 'username' not in session:
        return "Unauthorized", 401  # Ensure clinician is logged in

    data = request.json
    row_id = data["row_id"]
    clinician_name = session['username']  # Get logged-in clinician's username
    review = data["review"]
    status = "Verified" if data["status"] == "Verified" else "Not Verified"

    with sqlite3.connect(QUERY_DB) as conn:
        cursor = conn.cursor()

        # Store the clinician's username & modify verification format
        if status == "Verified":
            verification_text = f"Verified by {clinician_name}: {review}"
            cursor.execute("UPDATE queries SET verification=?, cli_username=?, status=? WHERE id=?",
                           (verification_text, clinician_name, status, row_id))
        else:
            verification_text = f"Reviewed by {clinician_name}: {review}"
            cursor.execute("UPDATE queries SET verification=?, status=? WHERE id=?",
                           (verification_text, status, row_id))

        conn.commit()

    return jsonify({"message": "Response verification updated successfully!"})

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Start Page
@app.route('/')
def start_page():
    return render_template("start_page.html")

@app.route('/patient_chat', methods=['POST'])
def patient_chat():
    if 'username' not in session:
        return "Unauthorized", 401  # Ensure user is logged in

    username = session['username']  # Store the Patient's username
    query = request.form.get('query')

    # Generate AI response
    ai_response = generate_ai_response(query)

    # Store query and response in QueryDataBase.sql with the Patient's username
    with sqlite3.connect(QUERY_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO queries (username, query, ai_response, verification, cli_username, status) VALUES (?, ?, ?, '', '', 'Not Verified')",
                       (username, query, ai_response))
        conn.commit()

    return ai_response

def generate_insights():
    with sqlite3.connect(QUERY_DB) as conn:
        cursor = conn.cursor()

        # Clinician-AI Agreement Rate
        cursor.execute("SELECT COUNT(*) FROM queries WHERE status='Verified'")
        verified = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM queries WHERE status='Not Verified'")
        not_verified = cursor.fetchone()[0]
        total_reviews = verified + not_verified

        if total_reviews > 0:
            labels = ['Verified AI Responses', 'Disagreed AI Responses']
            values = [verified, not_verified]
        else:
            labels = ['No Data']
            values = [1]

        plt.figure(figsize=(4, 4))
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=['green', 'red'])
        plt.title("Clinician-AI Agreement Rate")
        plt.savefig("static/agreement_rate.png")
        plt.close()

        # Clinician Workload
        cursor.execute("SELECT cli_username, COUNT(cli_username) FROM queries WHERE cli_username != '' GROUP BY cli_username")
        workload_data = cursor.fetchall()

        if workload_data:
            clinicians, counts = zip(*workload_data)
        else:
            clinicians, counts = ["No Data"], [1]

        plt.figure(figsize=(4, 4))
        plt.bar(clinicians, counts, color='blue')
        plt.xlabel("Clinicians")
        plt.ylabel("Responses Reviewed")
        plt.title("Clinician Workload")
        plt.xticks(rotation=45)
        plt.savefig("static/clinician_workload.png")
        plt.close()

# Route for Hospital Home Page
@app.route('/hospital_home')
def hospital_home():
    generate_insights()  # Generate graphs before rendering the page
    with sqlite3.connect(QUERY_DB) as conn:
        cursor = conn.cursor()

        # Most Common Queries
        cursor.execute("SELECT query, COUNT(query) FROM queries GROUP BY query ORDER BY COUNT(query) DESC LIMIT 5")
        common_queries = cursor.fetchall()

    return render_template("hospital_home.html", common_queries=common_queries)

def read_text_aloud(text):
    def speak():
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
    
    threading.Thread(target=speak, daemon=True).start()

@app.route('/read_aloud', methods=['POST'])
def read_aloud():
    data = request.json
    text = data.get("text", "")
    
    if text:
        read_text_aloud(text)
        return jsonify({"message": "Reading response aloud"})
    
    return jsonify({"error": "No text provided"}), 400

if __name__ == '__main__':
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)