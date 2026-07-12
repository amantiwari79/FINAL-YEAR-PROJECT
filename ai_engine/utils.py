import re
import os
import json
from django.conf import settings
from decouple import config
from google import genai
from google.genai import types

def get_gemini_client():
    """
    Initializes and returns the official Google GenAI Gemini client.
    Reads GEMINI_API_KEY from os.environ directly so admin panel updates
    take effect immediately without a server restart.
    Returns None if the key is not set or is a mock placeholder.
    """
    # os.environ checked first (live updates), then fall back to decouple/.env
    api_key = os.environ.get('GEMINI_API_KEY') or config('GEMINI_API_KEY', default='mock-key')
    if not api_key or 'mock' in api_key.lower() or api_key == 'your-gemini-api-key-here':
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return None

def parse_resume_with_ai(raw_text):
    """
    Parses resume raw text into structured JSON.
    Falls back to regex-based heuristics if no Gemini API key is set.
    """
    client = get_gemini_client()
    
    if not client:
        # High-fidelity mock parsing heuristic
        print("Gemini key not configured or mock. Using regex/heuristic parser.")
        
        # Regex extracts
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
        email = email_match.group(0) if email_match else "not-found@example.com"
        
        phone_match = re.search(r'\+?\d[\d\-\s\(\)]{8,}\d', raw_text)
        phone = phone_match.group(0) if phone_match else "Not Specified"
        
        name = "Candidate Name"
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        if lines:
            name = lines[0]
            
        common_skills = ['Python', 'Django', 'Flask', 'PostgreSQL', 'SQLite', 'React', 'Angular', 
                         'Vue', 'JavaScript', 'HTML', 'CSS', 'Git', 'Docker', 'AWS', 'Kubernetes',
                         'Machine Learning', 'AI', 'SQL', 'C++', 'Java']
        detected_skills = [skill for skill in common_skills if re.search(r'\b' + re.escape(skill) + r'\b', raw_text, re.IGNORECASE)]
        
        mock_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "summary": "Experienced software professional with passion for building scalable web services.",
            "skills": detected_skills if detected_skills else ["Python", "Django", "Web Development"],
            "education": [
                {
                    "school": "University of Technology",
                    "degree": "Bachelor of Science",
                    "major": "Computer Science",
                    "year": "2024"
                }
            ],
            "experience": [
                {
                    "company": "Tech Innovators Inc.",
                    "title": "Software Engineer Intern",
                    "dates": "2024 - Present",
                    "bullet_points": [
                        "Developed dynamic endpoints using Django Rest Framework, boosting efficiency by 15%.",
                        "Designed database schemas with PostgreSQL and integrated external APIs.",
                        "Participated in agile ceremonies and wrote test cases covering 90% codebase."
                    ]
                }
            ]
        }
        return mock_data

    # Real Gemini call
    try:
        prompt = f"""
        Analyze the following resume raw text and extract structured information.
        Return ONLY a JSON object matching this schema:
        {{
            "name": "Candidate Name",
            "email": "Email Address",
            "phone": "Phone Number",
            "summary": "Professional Summary",
            "skills": ["Skill1", "Skill2", ...],
            "education": [
                {{"school": "University Name", "degree": "Degree (e.g. BS)", "major": "Major (e.g. CS)", "year": "Graduation Year"}}
            ],
            "experience": [
                {{
                    "company": "Company Name", 
                    "title": "Job Title", 
                    "dates": "Start Date - End Date", 
                    "bullet_points": ["Action-oriented achievement bullet 1", "bullet 2"]
                }}
            ]
        }}

        Resume Raw Text:
        ---
        {raw_text}
        ---
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are an expert ATS data extraction parser. Output valid JSON matching the exact schema requested.",
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        parsed = json.loads(response.text)
        return parsed
    except Exception as e:
        print(f"Error parsing resume via Gemini: {e}")
        return {"error": "Failed to parse resume.", "raw_text_length": len(raw_text)}

def calculate_ats_score(resume_text, job_desc):
    """
    Compares the resume text against the job description.
    Returns: (score_int, feedback_dict)
    """
    client = get_gemini_client()
    
    if not client:
        print("Gemini key not configured or mock. Using heuristic ATS scoring.")
        score = 65
        missing = ["System Design", "Cloud Infrastructure", "Docker Containerization"]
        suggestions = [
            "Quantify accomplishments with metrics (e.g., 'improved performance by 20%')",
            "Add a dedicated Skills matrix matching keywords in the job description",
            "Describe deployment processes using containerization architectures"
        ]
        
        if job_desc:
            keywords = ['django', 'react', 'python', 'aws', 'docker', 'kubernetes', 'postgres', 'sql']
            matches = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', job_desc, re.IGNORECASE)]
            resume_matches = [kw for kw in matches if re.search(r'\b' + re.escape(kw) + r'\b', resume_text, re.IGNORECASE)]
            
            if matches:
                ratio = len(resume_matches) / len(matches)
                score = int(60 + (35 * ratio))
                missing = [kw.upper() for kw in matches if kw not in resume_matches]
                
        mock_feedback = {
            "overall_assessment": "The resume has strong formatting and covers core web development. However, it lacks specific keywords matching the cloud and systems criteria of this job description.",
            "matching_skills": ["Python", "Django", "SQL"],
            "missing_keywords": missing if missing else ["Docker", "AWS Deployments"],
            "suggestions": suggestions
        }
        return score, mock_feedback

    # Real Gemini ATS calculation
    try:
        prompt = f"""
        Compare the candidate's resume against the Job Description and provide a score out of 100 based on standard ATS parameters (keyword match, job title matching, required skills, formatting/readability).
        
        Provide a structured JSON output with the following keys:
        - "score": (integer between 0 and 100)
        - "overall_assessment": "paragraph summary of the match quality"
        - "matching_skills": ["Skill1", "Skill2"]
        - "missing_keywords": ["Keyword1", "Keyword2"]
        - "suggestions": ["Actionable tip 1", "tip 2"]

        Resume text:
        ---
        {resume_text}
        ---

        Job Description:
        ---
        {job_desc}
        ---
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a senior hiring manager and ATS screening system. Evaluate the match quality accurately and output only valid JSON.",
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        
        result = json.loads(response.text)
        score = int(result.get("score", 70))
        
        feedback_details = {
            "overall_assessment": result.get("overall_assessment", ""),
            "matching_skills": result.get("matching_skills", []),
            "missing_keywords": result.get("missing_keywords", []),
            "suggestions": result.get("suggestions", [])
        }
        
        return score, feedback_details
    except Exception as e:
        print(f"Error executing ATS score via Gemini: {e}")
        return 50, {"error": f"Failed to calculate ATS: {str(e)}"}

def rewrite_bullet_points(bullets):
    """
    Rewrites plain bullet points to high-impact achievements.
    """
    client = get_gemini_client()
    
    if not client:
        print("Gemini key not configured. Using mock rewrites.")
        rewritten = []
        for bullet in bullets:
            if not bullet.strip():
                continue
            rewritten.append({
                "original": bullet,
                "improved": f"Spearheaded core development cycle that elevated product delivery standards by 25% while deploying active components.",
                "reason": "Used strong action verb 'Spearheaded' and added a quantifiable impact metric (25%)."
            })
        return rewritten if rewritten else [
            {"original": "Wrote Django endpoints.", "improved": "Architected 15+ secure RESTful API endpoints using Django Rest Framework, slashing response times by 30%.", "reason": "Quantified scale and action."}
        ]

    try:
        prompt = f"""
        Rewrite the following resume bullet points to make them highly impactful, starting with strong action verbs (e.g. Spearheaded, Designed, Optimized) and incorporating metrics/quantifiable results wherever possible.
        
        Provide a structured JSON output with a "results" key containing a list of objects with:
        - "original": "the original bullet point"
        - "improved": "the rewritten bullet point"
        - "reason": "brief explanation of why this is better"

        Bullet points to improve:
        {json.dumps(bullets)}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a professional resume writer. Format your response as a JSON object.",
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        return json.loads(response.text).get("results", [])
    except Exception as e:
        print(f"Error rewriting bullet points via Gemini: {e}")
        return [{"original": b, "improved": b, "reason": "Failed to generate rewrite."} for b in bullets]

def generate_cover_letter(resume_text, job_title, company, job_desc):
    """
    Generates a personalized cover letter based on the candidate's CV and job criteria.
    """
    client = get_gemini_client()
    
    if not client:
        print("Gemini key not configured. Using mock cover letter.")
        return f"""Dear Hiring Team at {company},

I am writing to express my enthusiastic interest in the {job_title} position. Based on my technical background and parsed experience, I am confident in my ability to contribute effectively from day one.

In my previous roles, I focused on building clean backend logic, designing schemas, and collaborating with cross-functional teams to deploy features. These achievements align closely with the qualifications you are seeking for the {job_title} role.

Thank you for your time and consideration. I look forward to discussing how my skills and experience can help {company} achieve its goals.

Sincerely,
[Your Name]"""

    try:
        prompt = f"""
        Draft a highly professional and tailored cover letter for a candidate applying to the following position:
        - Job Title: {job_title}
        - Company: {company}
        
        Write the letter based on the candidate's resume achievements. Match the style and requirements of the target job description.
        
        Candidate Resume:
        ---
        {resume_text}
        ---
        
        Job Description:
        ---
        {job_desc}
        ---
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a professional CV editor and writer. Write a compelling, elegant cover letter in 3-4 paragraphs. Do not use place holders like [Insert Date] unless necessary. Focus on candidate value.",
                temperature=0.7
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating cover letter via Gemini: {e}")
        return f"Failed to generate cover letter. Technical error: {str(e)}"

def career_coach_chat(chat_history, user_message):
    """
    Acts as an AI career advisor responding to questions in a conversation history.
    """
    client = get_gemini_client()
    
    if not client:
        print("Gemini key not configured. Using mock career coach response.")
        return f"Hello! I'm your AI Career Coach. Since the Gemini API is currently offline/mocked, I can suggest some generic advice: for building a career as a developer, focus on building side projects, practicing code style, and documenting your database designs! Let me know if you have a specific question."

    try:
        contents = []
        for msg in chat_history:
            role = 'user' if msg.get("role") == 'user' else 'model'
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.get("content"))]))
            
        contents.append(types.Content(role='user', parts=[types.Part.from_text(text=user_message)]))
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="You are Resume Analysis AI+ Career Advisor, a highly helpful, empathetic, and knowledgeable career advisor. Give actionable advice on resume writing, job search, interview prep, and career growth.",
                temperature=0.7
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error in career coach chat via Gemini: {e}")
        return f"Sorry, I encountered an error answering your question. Error: {str(e)}"

def generate_interview_questions(resume_text, job_desc):
    """
    Generates tailored mock interview questions.
    """
    client = get_gemini_client()
    
    if not client:
        print("Gemini key not configured. Using mock interview questions.")
        return {
            "questions": [
                {"type": "Technical", "question": "Can you describe the lifecycle of a Django request and how middlewares process it?", "tips": "Detail request/response hooks, URL resolution, and view returns."},
                {"type": "Behavioral", "question": "Tell me about a time you had to deliver a feature under a tight deadline. How did you handle it?", "tips": "Use the STAR method: Situation, Task, Action, Result. Emphasize scoping."},
                {"type": "Situational", "question": "If a database query suddenly begins taking 10 seconds to execute, how would you diagnose and optimize it?", "tips": "Mention EXPLAIN, index analysis, connection pooling, and select_related/prefetch_related."}
            ]
        }

    try:
        prompt = f"""
        Generate 3 tailored interview questions based on the candidate's resume and target job requirements.
        One should be Technical, one Behavioral, and one Situational.
        
        Return ONLY a JSON object matching this schema:
        {{
            "questions": [
                {{"type": "Technical / Behavioral / Situational", "question": "The question text", "tips": "Helpful tip for answering"}}
            ]
        }}

        Candidate Resume:
        ---
        {resume_text}
        ---

        Target Job Description:
        ---
        {job_desc}
        ---
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a professional technical recruiter. Output only valid JSON.",
                response_mime_type="application/json",
                temperature=0.4
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error generating interview questions via Gemini: {e}")
        return {"questions": [{"type": "General", "question": "Tell me about yourself.", "tips": "Keep it under 2 minutes and focus on career highlights."}]}
