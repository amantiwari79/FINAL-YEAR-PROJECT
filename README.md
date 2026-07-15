# ResuMate AI+: AI-Powered Resume Analysis & Career Preparation Platform

An advanced, full-stack AI-driven web application designed to help job seekers optimize their resumes, match their profiles to job descriptions, generate customized resumes, and prepare for interviews using Google Gemini AI models.

---

## 🚀 Key Features

1. **Resume Parsing & Versioning**: Upload resumes in PDF/DOCX format, extract text automatically, and parse structure using AI. Maintain version history for each resume.
2. **ATS Scan & Matching**: Analyze how well a resume fits a specific job description. Get an overall percentage match score, identified keyword gaps, and actionable improvement recommendations.
3. **AI Career Coach Chatbot**: A real-time, session-based interactive chatbot providing expert guidance on career progression, salary negotiations, and resume advice.
4. **Mock Interview Preparation**: Generate dynamic, personalized interview questions and model answers tailored specifically to your resume and a target job role.
5. **AI Resume Generator**: Input raw career details (experience, education, skills) to instantly draft a clean, professional, ATS-optimized resume.
6. **Custom Administrative Panel**: View system logs, manage user accounts (active status, staff roles), and update API keys dynamically.

---

## 🛠️ Tech Stack

- **Backend Framework**: Python (Django 5.2+)
- **Database**: SQLite (Development-ready, lightweight relational database)
- **AI Integration**: Google Gemini API via `google-genai`
- **Text Extraction**: `pypdf` (for PDF files) and `docx2txt` (for MS Word files)
- **Configuration & Environment**: `python-decouple` (for `.env` settings management)
- **Frontend**: Responsive HTML5, Vanilla CSS3 (Custom styles in `static/css/style.css`), and JavaScript

---

## 📂 Project File Structure (For Viva Explanation)

The workspace has been restructured to have a clean, industry-standard layout:

```text
d:/new/
│
├── accounts/               # User Authentication & Custom Admin Panel App
│   ├── migrations/         # Database migration history
│   ├── forms.py            # User registration & profile forms
│   ├── models.py           # CustomUser model extending Django AbstractUser
│   ├── admin_views.py      # Admin control panel dashboard logic
│   └── views.py            # User login, registration, dashboard & logout views
│
├── ai_engine/              # AI Core App (Gemini Integrations)
│   ├── models.py           # ATS Feedback logs & AI API usage logs
│   ├── utils.py            # Main Gemini API wrapper calls (ATS score, Coach Chat, Interview Prep)
│   └── views.py            # View controllers for AI scans, career coach, & interview prep
│
├── resumes/                # Resume Management App
│   ├── models.py           # Resume and ResumeVersion models (tracks uploaded files)
│   ├── forms.py            # File upload validation form
│   ├── utils.py            # Document text parsers (PDF and DOCX text extractors)
│   └── views.py            # Upload, delete, details and PDF preview handlers
│
├── config/                 # Main Django Project Settings Folder
│   ├── settings.py         # Global configuration (installed apps, database config, static paths)
│   ├── urls.py             # Root URL routing configurations
│   └── wsgi.py / asgi.py   # Gateway interfaces for web servers
│
├── templates/              # Centralized HTML Template Files
│   ├── base.html           # Main base layout wrapper
│   ├── dashboard.html      # User workspace home view
│   ├── accounts/           # User login, registration, profile, and admin views
│   ├── ai_engine/          # Chatbot interface, ATS scans, and interview prep views
│   └── resumes/            # Resume upload, detail viewing, and deletion templates
│
├── static/                 # Static Assets (Images, Logo, Stylesheets)
│   └── css/style.css       # Core design styling sheet for the entire platform
│
├── media/                  # Uploaded Resume Documents (PDF/DOCX)
├── venv/                   # Python Virtual Environment (stores dependencies)
├── db.sqlite3              # Relational database file
├── .env                    # Environment variables (API keys, DEBUG mode, etc.)
├── manage.py               # Django command-line execution entry point
└── requirements.txt        # List of required Python packages
```

---

## 💻 Quick Start & Local Run Instructions

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Set Up Environment Variables
Create or open the `.env` file in the root directory and ensure it contains:
```env
DEBUG=True
SECRET_KEY=your-django-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Run Migrations (Prepare Database)
Apply the database schemas to set up user and feedback tables:
```bash
venv\Scripts\python manage.py migrate
```

### 4. Create Superuser (Admin Account)
To access the Django default admin panel (`/admin/`) or custom control panel (`/admin-panel/`):
```bash
venv\Scripts\python manage.py createsuperuser
```

### 5. Start the Server
Run the local development server:
```bash
venv\Scripts\python manage.py runserver
```
Open your browser and navigate to `http://127.0.0.1:8000/`.
