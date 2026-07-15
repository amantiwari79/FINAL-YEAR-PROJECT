import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from resumes.models import Resume, ResumeVersion
from .models import ATSFeedback, AIActionLog
from .utils import (
    calculate_ats_score,
    career_coach_chat,
    generate_interview_questions,
    generate_resume_from_details
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
            
        t0 = time.time()
        score, feedback_details = calculate_ats_score(resume.raw_text, job_description)
        latency = round(time.time() - t0, 2)
        
        # Save to database
        feedback_report = ATSFeedback.objects.create(
            resume=resume,
            score=score,
            job_description=job_description,
            feedback=feedback_details
        )
        # Log AI action
        AIActionLog.objects.create(
            action='ats_scan',
            target_name=f"{resume.user.first_name} {resume.user.last_name} – {resume.title}",
            tokens_used=len(resume.raw_text.split()) + len(job_description.split()),
            latency_ms=latency,
            status='success'
        )
        messages.success(request, 'ATS scan completed successfully!')

    # Get last scan if available
    latest_scan = resume.feedbacks.first()
    active_report = feedback_report or latest_scan

    # Build score history (last 6 scans) for line chart
    history_qs = resume.feedbacks.order_by('created_at')[:6]
    score_history = [{'score': f.score, 'date': f.created_at.strftime('%b')} for f in history_qs]

    context = {
        'resume': resume,
        'feedback_report': active_report,
        'score_history': score_history,
    }
    return render(request, 'ai_engine/ats_scan.html', context)




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
            t0 = time.time()
            assistant_response = career_coach_chat(chat_history[:-1], user_message)
            latency = round(time.time() - t0, 2)
            chat_history.append({"role": "assistant", "content": assistant_response})
            
            # Save history back to session
            request.session['chat_history'] = chat_history
            request.session.modified = True
            AIActionLog.objects.create(
                action='career_coach',
                target_name=f"{request.user.first_name} {request.user.last_name}",
                tokens_used=len(user_message.split()),
                latency_ms=latency,
                status='success'
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return JsonResponse({
                    'status': 'success',
                    'response': assistant_response
                })
            
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
            t0 = time.time()
            prep_data = generate_interview_questions(resume.raw_text, job_description)
            latency = round(time.time() - t0, 2)
            AIActionLog.objects.create(
                action='interview_prep',
                target_name=f"{resume.user.first_name} {resume.user.last_name} – {resume.title}",
                tokens_used=len(resume.raw_text.split()) + len(job_description.split()),
                latency_ms=latency,
                status='success'
            )
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
    Results are displayed inline on the same page.
    """
    resumes = Resume.objects.filter(user=request.user)
    match_result = None
    selected_resume = None

    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        job_description = request.POST.get('job_description', '').strip()

        if not resume_id or not job_description:
            messages.error(request, 'Please select a resume and provide a job description.')
        else:
            selected_resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
            t0 = time.time()
            score, feedback_details = calculate_ats_score(selected_resume.raw_text, job_description)
            latency = round(time.time() - t0, 2)

            # Persist to DB
            ATSFeedback.objects.create(
                resume=selected_resume,
                score=score,
                job_description=job_description,
                feedback=feedback_details
            )
            AIActionLog.objects.create(
                action='job_matching',
                target_name=f"{request.user.first_name} {request.user.last_name} – {selected_resume.title}",
                tokens_used=len(selected_resume.raw_text.split()) + len(job_description.split()),
                latency_ms=latency,
                status='success'
            )
            match_result = {
                'score': score,
                'feedback': feedback_details,
                'resume_title': selected_resume.title,
                'job_description': job_description,
            }

    return render(request, 'ai_engine/job_matching.html', {
        'resumes': resumes,
        'match_result': match_result,
        'selected_resume': selected_resume,
    })

@login_required
def resume_generator_view(request):
    """
    Builds an ATS-friendly resume draft from user-entered career details.
    """
    generated_resume = None
    form_data = {
        'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
        'email': request.user.email,
    }

    if request.method == 'POST':
        fields = [
            'full_name', 'email', 'phone', 'location', 'links', 'target_role',
            'skills', 'experience', 'projects', 'education', 'certifications',
            'achievements'
        ]
        form_data = {field: request.POST.get(field, '').strip() for field in fields}

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')

        if not form_data.get('full_name') or not form_data.get('target_role') or not form_data.get('skills'):
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Please add your name, target role, and key skills.'}, status=400)
            messages.error(request, 'Please add your name, target role, and key skills.')
        else:
            t0 = time.time()
            generated_resume = generate_resume_from_details(form_data)
            latency = round(time.time() - t0, 2)
            AIActionLog.objects.create(
                action='resume_generator',
                target_name=f"{request.user.first_name} {request.user.last_name} - {form_data.get('target_role')}",
                tokens_used=sum(len(value.split()) for value in form_data.values()),
                latency_ms=latency,
                status='success'
            )
            if is_ajax:
                return JsonResponse({'status': 'success', 'resume': generated_resume})
            messages.success(request, 'Resume draft generated successfully!')

    return render(request, 'ai_engine/resume_generator.html', {
        'form_data': form_data,
        'generated_resume': generated_resume,
    })

