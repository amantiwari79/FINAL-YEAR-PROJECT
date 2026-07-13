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

def safe_json_loads(text):
    """
    Safely loads JSON from string, handling common LLM response formatting issues
    such as markdown block formatting (```json ... ```).
    """
    if not text:
        return {}
    cleaned = text.strip()
    # Strip markdown block formatting if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:json)?\n', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\n```$', '', cleaned)
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: extract JSON structure
        match = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        raise

def parse_resume_with_ai(raw_text):
    """
    Parses resume raw text into structured JSON.
    Falls back to regex-based heuristics if no Gemini API key is set or if the call fails.
    """
    client = get_gemini_client()
    if client:
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
            return safe_json_loads(response.text)
        except Exception as e:
            print(f"Error parsing resume via Gemini: {e}. Falling back to heuristic parser.")

    # High-fidelity mock parsing heuristic fallback
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

def calculate_ats_score(resume_text, job_desc):
    """
    Compares the resume text against the job description.
    Returns: (score_int, feedback_dict) with rich analytics data.
    """
    client = get_gemini_client()
    if client:
        try:
            prompt = f"""
            Compare the candidate's resume against the Job Description and provide a score out of 100 based on standard ATS parameters.
            
            Return ONLY a JSON object with these exact keys:
            {{
                "score": <integer 0-100 overall ATS match>,
                "overall_assessment": "paragraph summary",
                "matching_skills": ["Skill1", "Skill2"],
                "missing_keywords": ["Keyword1", "Keyword2"],
                "suggestions": ["Actionable tip 1", "tip 2"],
                "score_breakdown": {{
                    "ats_score": <0-100>,
                    "skills": <0-100>,
                    "experience": <0-100>,
                    "education": <0-100>,
                    "formatting": <0-100>,
                    "readability": <0-100>
                }},
                "grammar_score": <0-100>,
                "skills_distribution": {{
                    "technical": <percentage>,
                    "soft": <percentage>,
                    "tools": <percentage>,
                    "languages": <percentage>
                }}
            }}

            Resume:
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
                    system_instruction="You are a senior hiring manager and ATS screening system. Evaluate accurately and output only valid JSON.",
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            result = safe_json_loads(response.text)
            score = int(result.get("score", 70))
            breakdown = result.get("score_breakdown", {})
            feedback_details = {
                "overall_assessment": result.get("overall_assessment", ""),
                "matching_skills": result.get("matching_skills", []),
                "missing_keywords": result.get("missing_keywords", []),
                "suggestions": result.get("suggestions", []),
                "score_breakdown": {
                    "ats_score": breakdown.get("ats_score", score),
                    "skills": breakdown.get("skills", 70),
                    "experience": breakdown.get("experience", 68),
                    "education": breakdown.get("education", 80),
                    "formatting": breakdown.get("formatting", 75),
                    "readability": breakdown.get("readability", 72),
                },
                "grammar_score": int(result.get("grammar_score", 80)),
                "skills_distribution": result.get("skills_distribution", {
                    "technical": 57, "soft": 21, "tools": 14, "languages": 8
                }),
            }
            return score, feedback_details
        except Exception as e:
            print(f"Error executing ATS score via Gemini: {e}. Falling back to heuristic scoring.")

    # Heuristic fallback: Dynamically extract keywords and match scores based on resume and job description content
    all_keywords = [
        'python', 'django', 'flask', 'fastapi', 'javascript', 'typescript', 'react', 'angular', 'vue',
        'node', 'express', 'html', 'css', 'sass', 'bootstrap', 'tailwind', 'postgres', 'postgresql',
        'mysql', 'sqlite', 'mongodb', 'redis', 'elasticsearch', 'docker', 'kubernetes', 'aws', 'gcp',
        'azure', 'git', 'github', 'ci/cd', 'jenkins', 'devops', 'linux', 'nginx', 'apache', 'graphql',
        'rest api', 'system design', 'agile', 'scrum', 'pytest', 'unit testing', 'machine learning', 
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'data science', 'tableau', 
        'c', 'c++', 'c#', 'java', 'kotlin', 'swift', 'go', 'golang', 'rust', 'php', 'ruby'
    ]
    
    # Extract keywords from job description
    job_desc_lower = job_desc.lower()
    job_keywords = [kw for kw in all_keywords if re.search(r'\b' + re.escape(kw) + r'\b', job_desc_lower)]
    
    if not job_keywords:
        job_keywords = ['python', 'django', 'javascript', 'react', 'sql', 'git', 'rest api']
        
    # Extract keywords from resume
    resume_lower = resume_text.lower()
    matching_skills = [kw.title() for kw in job_keywords if re.search(r'\b' + re.escape(kw) + r'\b', resume_lower)]
    missing_keywords = [kw.title() for kw in job_keywords if kw.title() not in matching_skills]
    
    # Calculate match ratio and score
    match_ratio = len(matching_skills) / len(job_keywords) if job_keywords else 0.5
    score = int(50 + (45 * match_ratio))
    score = min(max(score, 30), 98)
    
    # Generate custom suggestions
    suggestions = [
        "Quantify your accomplishments with clear business metrics (e.g., 'improved query performance by 30%').",
        "Begin bullet points with powerful action verbs like 'Led', 'Optimized', or 'Architected'."
    ]
    if missing_keywords:
        suggestions.insert(0, f"Integrate these missing key skills into your experience section: {', '.join(missing_keywords[:3])}.")
    if score < 70:
        suggestions.append(f"Tailor your summary to highlight core matching technologies like {', '.join(matching_skills[:2]) if matching_skills else 'software development'}.")
        
    # Generate overall assessment
    if matching_skills:
        match_str = f"The resume demonstrates good alignment with several target requirements, including: {', '.join(matching_skills[:3])}."
    else:
        match_str = "The resume covers general software development concepts but has very limited keyword overlap with the target job description."
        
    if missing_keywords:
        gap_str = f" However, critical gaps were detected in: {', '.join(missing_keywords[:3])}. Addressing these will significantly boost your match rate."
    else:
        gap_str = " No significant keyword gaps were detected. The candidate is a strong fit for the technical stack."
        
    overall_assessment = match_str + gap_str
    
    grammar_score = 88 if "write" in resume_lower or "develop" in resume_lower else 78
    if score < 60:
        grammar_score = 75
        
    mock_feedback = {
        "overall_assessment": overall_assessment,
        "matching_skills": matching_skills,
        "missing_keywords": missing_keywords,
        "suggestions": suggestions,
        "score_breakdown": {
            "ats_score": score,
            "skills": min(score + 6, 98),
            "experience": max(score - 3, 30),
            "education": 85 if any(x in resume_lower for x in ['bachelor', 'degree', 'university', 'b.s', 'b.tech', 'm.s']) else 60,
            "formatting": 80,
            "readability": 82 if len(resume_text) < 4000 else 72,
        },
        "grammar_score": grammar_score,
        "skills_distribution": {
            "technical": 60 if len(matching_skills) > 2 else 45,
            "soft": 20,
            "tools": 15,
            "languages": 5
        },
    }
    return score, mock_feedback

def rewrite_bullet_points(bullets):
    """
    Rewrites plain bullet points to high-impact achievements.
    """
    client = get_gemini_client()
    if client:
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
            return safe_json_loads(response.text).get("results", [])
        except Exception as e:
            print(f"Error rewriting bullet points via Gemini: {e}. Falling back to mock rewrites.")

    # Fallback mock rewrites
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

def generate_cover_letter(resume_text, job_title, company, job_desc):
    """
    Generates a personalized cover letter based on the candidate's CV and job criteria.
    """
    client = get_gemini_client()
    if client:
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
            print(f"Error generating cover letter via Gemini: {e}. Falling back to mock letter.")

    # Fallback mock cover letter
    return f"""Dear Hiring Team at {company},

I am writing to express my enthusiastic interest in the {job_title} position. Based on my technical background and parsed experience, I am confident in my ability to contribute effectively from day one.

In my previous roles, I focused on building clean backend logic, designing schemas, and collaborating with cross-functional teams to deploy features. These achievements align closely with the qualifications you are seeking for the {job_title} role.

Thank you for your time and consideration. I look forward to discussing how my skills and experience can help {company} achieve its goals.

Sincerely,
[Your Name]"""

def career_coach_chat(chat_history, user_message):
    """
    Acts as an AI career advisor responding to questions in a conversation history.
    """
    client = get_gemini_client()
    if client:
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
                    system_instruction="You are Resume Analysis AI+ Career Advisor, a highly helpful, empathetic, and knowledgeable career advisor. Give actionable advice on resume writing, job search, interview prep, and career growth. Use clear markdown formatting (such as bullet points, bold text, and section headers) to make your replies structured and readable.",
                    temperature=0.7
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error in career coach chat via Gemini: {e}. Falling back to mock advisor.")

    # Fallback mock advisor response
    return "Hello! I'm your **AI Career Coach**. Since the Gemini API is currently offline/mocked, I can suggest some generic advice:\n\n* **Side Projects**: Build real-world projects to showcase your skills.\n* **Code Style**: Practice clean, pep8/standard code styling.\n* **Database Design**: Document your database designs and schemas.\n\nLet me know if you have a specific question!"

def generate_interview_questions(resume_text, job_desc):
    """
    Generates tailored mock interview questions.
    """
    client = get_gemini_client()
    if client:
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
            return safe_json_loads(response.text)
        except Exception as e:
            print(f"Error generating interview questions via Gemini: {e}. Falling back to mock questions.")

    # Fallback mock interview questions
    return {
        "questions": [
            {"type": "Technical", "question": "Can you describe the lifecycle of a Django request and how middlewares process it?", "tips": "Detail request/response hooks, URL resolution, and view returns."},
            {"type": "Behavioral", "question": "Tell me about a time you had to deliver a feature under a tight deadline. How did you handle it?", "tips": "Use the STAR method: Situation, Task, Action, Result. Emphasize scoping."},
            {"type": "Situational", "question": "If a database query suddenly begins taking 10 seconds to execute, how would you diagnose and optimize it?", "tips": "Mention EXPLAIN, index analysis, connection pooling, and select_related/prefetch_related."}
        ]
    }

def improve_grammar(text_blocks):
    """
    Corrects grammar, spelling, and tone in resume text blocks.
    Returns a list of dicts with 'original', 'corrected', 'changes' keys.
    Falls back to rule-based heuristics if API is unavailable.
    """
    client = get_gemini_client()
    if client:
        try:
            prompt = f"""
            You are a professional resume editor. For each of the following text blocks, fix grammar, spelling, punctuation, and professional tone.
            
            Return ONLY a JSON object matching this schema:
            {{
                "results": [
                    {{
                        "original": "the original text",
                        "corrected": "the corrected version",
                        "changes": ["Change 1 description", "Change 2 description"]
                    }}
                ]
            }}

            Text blocks to correct:
            {json.dumps(text_blocks)}
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a professional resume editor and grammar expert. Fix grammar, spelling, and improve professional tone. Output only valid JSON.",
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            return safe_json_loads(response.text).get("results", [])
        except Exception as e:
            print(f"Error improving grammar via Gemini: {e}. Falling back to heuristic grammar fixer.")

    # Heuristic fallback - basic common corrections
    results = []
    common_fixes = [
        (r'\bi\b', 'I'),
        (r'\bdont\b', "don't"),
        (r'\bcant\b', "can't"),
        (r'\bwont\b', "won't"),
        (r'\bdidnt\b', "didn't"),
        (r'\bcouldnt\b', "couldn't"),
        (r'\bwouldnt\b', "wouldn't"),
        (r'\bshouldnt\b', "shouldn't"),
        (r'\bisnt\b', "isn't"),
        (r'\bwasnt\b', "wasn't"),
    ]
    for block in text_blocks:
        if not block.strip():
            continue
        corrected = block
        changes_made = []
        # Capitalize first letter
        if corrected and corrected[0].islower():
            corrected = corrected[0].upper() + corrected[1:]
            changes_made.append("Capitalized the first letter of the sentence.")
        # Apply basic contractions
        for pattern, replacement in common_fixes:
            if re.search(pattern, corrected, re.IGNORECASE):
                corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
                changes_made.append(f"Fixed contraction: applied '{replacement}'.")
        # Add period at end if missing
        if corrected and corrected[-1] not in '.!?':
            corrected += '.'
            changes_made.append("Added missing period at end of sentence.")
        if not changes_made:
            changes_made = ["Reviewed text — no critical grammar issues detected."]
        results.append({
            "original": block,
            "corrected": corrected,
            "changes": changes_made
        })
    return results if results else [{
        "original": "Sample text without proper grammar",
        "corrected": "Sample text with proper grammar.",
        "changes": ["Added missing period.", "Improved sentence structure."]
    }]
