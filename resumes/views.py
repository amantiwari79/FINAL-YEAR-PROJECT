from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Resume, ResumeVersion
from .forms import ResumeUploadForm
from .utils import extract_text_from_file
from ai_engine.utils import parse_resume_with_ai

@login_required
def upload_resume(request):
    """
    Uploads a new resume and extracts its text contents to start tracking it.
    """
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.current_version = 1
            resume.save()

            # Extract raw text content
            uploaded_file = request.FILES.get('file')
            # Seek to start of file just in case
            uploaded_file.seek(0)
            resume.raw_text = extract_text_from_file(uploaded_file, uploaded_file.name)
            resume.parsed_data = parse_resume_with_ai(resume.raw_text)
            resume.save()

            # Create initial ResumeVersion
            ResumeVersion.objects.create(
                resume=resume,
                version_number=1,
                file=resume.file,
                raw_text=resume.raw_text,
                parsed_data=resume.parsed_data
            )

            messages.success(request, _('Resume uploaded and parsed successfully!'))
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = ResumeUploadForm()
        
    return render(request, 'resumes/upload.html', {'form': form})

@login_required
def upload_new_version(request, pk):
    """
    Uploads a new version of an existing resume.
    """
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, _('Please select a file to upload.'))
            return redirect('resume_detail', pk=pk)
            
        # Standard validation since we are not using a model form for this quick view
        import os
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.pdf', '.docx']:
            messages.error(request, _('Unsupported file extension. Only PDF and DOCX files are allowed.'))
            return redirect('resume_detail', pk=pk)
            
        if file.size > 5 * 1024 * 1024:
            messages.error(request, _('File size exceeds the 5MB limit.'))
            return redirect('resume_detail', pk=pk)

        # Extract text from the new version
        file.seek(0)
        raw_text = extract_text_from_file(file, file.name)
        parsed_data = parse_resume_with_ai(raw_text)
        
        # Increment version
        new_version_number = resume.current_version + 1
        
        # Create ResumeVersion
        version = ResumeVersion.objects.create(
            resume=resume,
            version_number=new_version_number,
            file=file,
            raw_text=raw_text,
            parsed_data=parsed_data
        )
        
        # Update parent Resume
        resume.current_version = new_version_number
        resume.file = version.file
        resume.raw_text = version.raw_text
        resume.parsed_data = version.parsed_data
        resume.save()
        
        messages.success(request, f'Successfully uploaded version {new_version_number}!')
        return redirect('resume_detail', pk=pk)

@login_required
def resume_detail(request, pk):
    """
    Displays the details, preview, and versions list of a specific resume.
    """
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    versions = resume.versions.all()
    
    # We will fetch ATS feedbacks once the ai_engine app is configured
    feedbacks = []
    if hasattr(resume, 'feedbacks'):
        feedbacks = resume.feedbacks.all()

    context = {
        'resume': resume,
        'versions': versions,
        'feedbacks': feedbacks,
    }
    return render(request, 'resumes/detail.html', context)

@login_required
def delete_resume(request, pk):
    """
    Deletes the resume and all associated files.
    """
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        resume.delete()
        messages.success(request, _('Resume deleted successfully.'))
        return redirect('dashboard')
    return render(request, 'resumes/delete_confirm.html', {'resume': resume})
