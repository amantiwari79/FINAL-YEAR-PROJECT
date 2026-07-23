# AI-Powered Resume Analysis & Optimization Platform

### 🎓 Final Year Project: AI-Based Resume Parser, ATS Scorer, & Career Assistant

A comprehensive, state-of-the-art web application built with **Django** and powered by the **Google Gemini AI Engine** (via `google-genai` SDK). This platform is designed to help job seekers upload their resumes (in PDF or DOCX), parse them, analyze their compatibility with target job descriptions (ATS scoring), generate professional resumes, and optimize their career trajectory with targeted AI features.

---

## 🚀 Key Features

### 1. User Authentication & Profile

- **Custom User Model**: Uses email address as the primary identifier instead of a username.
- **Profile Customization**: Support for user avatars and profile pictures.

### 2. Resume Parsing & Version Control

- **Multiformat Support**: Extracts text from both PDF (`pypdf`) and Word (`docx2txt`) documents.
- **Resume History & Tracking**: Stores upload history and maintains multiple versions of resumes (`ResumeVersion`).

### 3. AI-Driven Analytics & ATS Scorer

- **ATS Scan & Score**: Rates resume alignment against specific job descriptions using Gemini AI.
- **Resume Enhancer**:
  - **Bullet Improver**: Suggests high-impact action verbs and phrasing.
  - **Cover Letter Generator**: Auto-generates tailored cover letters for roles.
  - **Career Coach**: Provides personalized feedback based on resume gaps.
  - **Interview Prep**: Creates role-specific interview questions.
  - **Skills Gap Analysis**: Maps resume skills against target jobs and highlights missing areas.

### 4. Custom Resume Generator

- **Multi-template Support**: Generates resumes in various styles: _Modern, Minimal, Corporate, Executive, and Creative_.
- **Tailored Outputs**: Generates structured, ATS-friendly JSON resume schemas ready for exporting.

### 5. Admin & Monitoring Dashboard

- **Admin Panel Access**: Pre-registered tables inside Django admin for managing users, resumes, feedback, and logs.
- **AI Operation Logs**: Tracks tokens used, API latency (ms), and statuses (`Success`, `Error`, `Mocked`) of all GenAI calls for real-time monitoring.
- **Database CLI Utility**: A built-in [db.py](file:///d:/new/db.py) tool to browse database tables and schemas directly from the command line.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12.x, Django 5.2.x
- **Database**: SQLite (Local development), PostgreSQL-ready (`psycopg2-binary`, `dj-database-url`)
- **AI SDK**: Google GenAI SDK (`google-genai`)
- **Utilities**: PyPDF (PDF text extraction), docx2txt (DOCX text extraction), Python-Decouple (Environment settings), WhiteNoise (Production static file server)
- **Frontend**: HTML5, Vanilla CSS3, Javascript (Dynamic client-side actions)

---

## 📂 Project Structure

```text
├── accounts/           # User authentication, profiles, & Custom User Model
├── ai_engine/          # Gemini AI API integrations, ATS analysis, Resume Generation, & AI Logs
├── resumes/            # Resume upload handling, parsing engine, & version control
├── config/             # Django core settings, routing, WSGI/ASGI configurations
├── templates/          # HTML templates for views
├── static/             # CSS styling, Javascript logic, and assets
├── media/              # User-uploaded files (resumes, profile pictures)
├── db.sqlite3          # SQLite Database file
├── db.py               # Local Database CLI Inspection Utility
├── manage.py           # Django administrative entry point
└── requirements.txt    # Python dependencies list
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.12.x installed.
- A Gemini API Key (Get one from [Google AI Studio](https://aistudio.google.com/)).

### Step-by-Step Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd FINAL-YEAR-PROJECT
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Settings Setup:**
   Create a `.env` file in the root directory (same folder as `manage.py`):

   ```ini
   DEBUG=True
   SECRET_KEY=your-django-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   ```

5. **Run Migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser (Admin account):**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```

Now open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser to view the application, and go to [http://127.0.0.1:5000/admin/](http://127.0.0.1:5000/admin/) to access the Django Administration Dashboard.

---

## 🗃️ Command Line Tools

### Database CLI Inspector

If you want to view your SQLite database tables or schema without opening Django or external database browsers, run:

```bash
python db.py
```

This utility allows you to list all tables, check column definitions, and query the first few rows of any table interactively.
