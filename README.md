# Hackenza-2025-Patient-Clinician-Portal_Wild-Card

# Patient-Clinician Portal

## Overview
This project is a **Patient-Clinician Portal (PCP)** that facilitates communication between patients and clinicians using AI-generated responses. The system allows users to sign up as a **patient, clinician, or hospital administrator** and interact with AI for medical inquiries. Clinicians can verify AI responses, and hospitals can monitor statistics related to AI response accuracy and clinician workload.

## Features
- **User Authentication** (Signup/Login for Patients, Clinicians, and Hospitals)
- **AI-Powered Chatbot** for medical inquiries
- **Clinician Review & Verification** of AI-generated responses
- **Hospital Dashboard** displaying analytics on AI accuracy and clinician workload
- **Voice Output** to read AI responses aloud
- **Data Storage in SQLite Databases**
- **Web-based Interface (Flask & HTML/CSS)**

## Tech Stack
- **Backend:** Flask, SQLite
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **AI Model:** Google Gemini API
- **Other Dependencies:** Matplotlib, Pyttsx3 (Text-to-Speech)

## Installation
### 1. Clone the Repository
```bash
    git clone https://github.com/your-repo/pcp-portal.git
    cd pcp-portal
```
### 2. Create a Virtual Environment
```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 3. Install Dependencies
```bash
    pip install -r requirements.txt
```
### 4. Set Up Google AI API Key
Replace `YOUR_API_KEY` in `Server.py` with your Google Gemini API key.

### 5. Run the Application
```bash
    python Server.py
```
Open `http://127.0.0.1:5000/` in your browser.

## File Structure
```
├── Server.py                # Flask backend
├── GrandDataBase.sql        # SQLite database for user management
├── QueryDataBase.sql        # SQLite database for query storage
├── templates/               # HTML files for different user dashboards
│   ├── start_page.html      # Home page
│   ├── login.html           # Login page
│   ├── signup.html          # Signup page
│   ├── patient_home.html    # Patient dashboard
│   ├── clinician_home.html  # Clinician dashboard
│   ├── hospital_home.html   # Hospital dashboard
├── static/                  # Static files (CSS, JS, images, etc.)
```

## Usage
1. **Signup/Login** as a **patient, clinician, or hospital admin**.
2. **Patients** submit medical queries to the AI chatbot.
3. **Clinicians** review AI responses and verify their accuracy.
4. **Hospitals** can monitor verification statistics and common queries.

## License
MIT License

## Contributors
- Your Name (@yourgithub)
- Other contributors

