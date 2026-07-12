from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from resumes.models import Resume, ResumeVersion
from .models import ATSFeedback
from .utils import (
    calculate_ats_score,
    rewrite_bullet_points,
    generate_cover_letter,
    career_coach_chat,
    generate_interview_questions
)

@login_required
def ats_scan(request, resume_id):
    """
    Form to input job description and display the calculated ATS score feedback.
    """
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    feedback_report = None
    
    if request.method == 'POST':
        job_description = request.POST.get('job_description', '').strip()
        if not job_description:
            messages.error(request, 'Please provide a job description.')
            return redirect('ats_scan', resume_id=resume_id)
            
        score, feedback_details = calculate_ats_score(resume.raw_text, job_description)
        
        # Save to database
        feedback_report = ATSFeedback.objects.create(
            resume=resume,
            score=score,
            job_description=job_description,
            feedback=feedback_details
        )
        messages.success(request, 'ATS scan completed successfully!')
        
    # Get last scan if available
    latest_scan = resume.feedbacks.first()
    
    context = {
        'resume': resume,
        'feedback_report': feedback_report or latest_scan,
    }
    return render(request, 'ai_engine/ats_scan.html', context)

@login_required
def bullet_improver(request, resume_id):
    """
    Extracts and rewrites experience bullet points using AI metrics.
    """
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    
    # Try to load bullets from parsed experience
    experience_list = resume.parsed_data.get('experience', [])
    bullets = []
    for exp in experience_list:
        bullets.extend(exp.get('bullet_points', []))
        
    # If no bullets parsed, provide standard default list for demo/editor
    if not bullets:
        bullets = [
            "Responsible for building Django APIs.",
            "Helped fix bugs and database queries.",
            "Wrote unit tests for the frontend."
        ]
        
    rewritten_bullets = None
    if request.method == 'POST':
        # User submitted bullets to improve
        submitted_bullets = request.POST.getlist('bullets')
        if not submitted_bullets:
            # Fallback if text field is used
            raw_bullets_text = request.POST.get('raw_bullets', '')
            submitted_bullets = [b.strip() for b in raw_bullets_text.split('\n') if b.strip()]
            
        if submitted_bullets:
            rewritten_bullets = rewrite_bullet_points(submitted_bullets)
            messages.success(request, 'AI rewrite suggestion generated!')
            
    context = {
        'resume': resume,
        'original_bullets': bullets,
        'rewritten_bullets': rewritten_bullets
    }
    return render(request, 'ai_engine/bullet_improver.html', context)

@login_required
def cover_letter_view(request, resume_id):
    """
    Form to input job details and render a custom AI-generated cover letter.
    """
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    cover_letter = None
    
    if request.method == 'POST':
        job_title = request.POST.get('job_title', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        job_description = request.POST.get('job_description', '').strip()
        
        if not job_title or not company_name:
            messages.error(request, 'Job Title and Company Name are required.')
        else:
            cover_letter = generate_cover_letter(resume.raw_text, job_title, company_name, job_description)
            messages.success(request, 'Cover letter generated successfully!')
            
    context = {
        'resume': resume,
        'cover_letter': cover_letter,
    }
    return render(request, 'ai_engine/cover_letter.html', context)

@login_required
def career_coach_view(request):
    """
    Provides a chatbot interface for interactive career coaching.
    """
    # Manage history in user session
    if 'chat_history' not in request.session:
        request.session['chat_history'] = [
            {"role": "assistant", "content": "Hi there! I am your AI Career Coach. Ask me anything about resume writing, interview preparation, career paths, or salary negotiations."}
        ]
        
    chat_history = request.session['chat_history']
    
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            # Append user message
            chat_history.append({"role": "user", "content": user_message})
            
            # Generate assistant response
            assistant_response = career_coach_chat(chat_history[:-1], user_message)
            chat_history.append({"role": "assistant", "content": assistant_response})
            
            # Save history back to session
            request.session['chat_history'] = chat_history
            request.session.modified = True
            
    # Clear chat trigger
    if request.GET.get('clear') == '1':
        request.session['chat_history'] = [
            {"role": "assistant", "content": "Hi there! I am your AI Career Coach. Ask me anything about resume writing, interview preparation, career paths, or salary negotiations."}
        ]
        return redirect('career_coach')
        
    context = {
        'chat_history': chat_history
    }
    return render(request, 'ai_engine/career_coach.html', context)

@login_required
def interview_prep_view(request, resume_id):
    """
    Generates mock interview questions and tips based on resume and target job.
    """
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    prep_data = None
    
    if request.method == 'POST':
        job_description = request.POST.get('job_description', '').strip()
        if job_description:
            prep_data = generate_interview_questions(resume.raw_text, job_description)
            messages.success(request, 'Mock interview questions generated!')
            
    context = {
        'resume': resume,
        'prep_data': prep_data
    }
    return render(request, 'ai_engine/interview_prep.html', context)

@login_required
def job_matching_view(request):
    """
    Renders general Job Matching dashboard where candidates select a resume and paste a job description.
    """
    resumes = Resume.objects.filter(user=request.user)
    
    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        job_description = request.POST.get('job_description', '').strip()
        
        if not resume_id or not job_description:
            messages.error(request, 'Please select a resume and provide a job description.')
            return redirect('job_matching')
            
        resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
        score, feedback_details = calculate_ats_score(resume.raw_text, job_description)
        
        # Save to database
        ATSFeedback.objects.create(
            resume=resume,
            score=score,
            job_description=job_description,
            feedback=feedback_details
        )
        messages.success(request, f'Job matching scan for "{resume.title}" completed successfully!')
        return redirect('ats_scan', resume_id=resume.pk)
        
    return render(request, 'ai_engine/job_matching.html', {'resumes': resumes})
