from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import RegisterForm, ResumeUploadForm, JobDescriptionForm
from .models import Resume, Analysis
from .utils.pdf_reader import extract_text_from_pdf, count_pdf_pages
from .utils.skill_extractor import extract_skills
from .utils.scoring import (
    compute_similarity_score,
    compute_skill_overlap_score,
    compute_overall_score,
)
from .utils.ats_checker import check_ats_compatibility
from .utils.suggestions import generate_suggestions


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Account created successfully. Welcome!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    upload_form = ResumeUploadForm()
    return render(request, 'core/dashboard.html', {
        'resumes': resumes,
        'upload_form': upload_form,
    })


@login_required
@require_POST
def upload_resume(request):
    form = ResumeUploadForm(request.POST, request.FILES)
    if form.is_valid():
        resume = form.save(commit=False)
        resume.user = request.user
        resume.original_filename = form.cleaned_data['file'].name
        resume.save()

        # Extract text immediately so later steps don't re-parse the PDF.
        resume.file.open('rb')
        try:
            extracted = extract_text_from_pdf(resume.file)
        finally:
            resume.file.close()

        resume.extracted_text = extracted
        resume.save()

        if not extracted.strip():
            messages.warning(
                request,
                "We couldn't extract any text from this PDF. It may be a scanned "
                "image — try a text-based PDF instead."
            )
        else:
            messages.success(request, 'Resume uploaded successfully.')
        return redirect('analyze', resume_id=resume.id)
    else:
        messages.error(request, 'Upload failed: ' + ' '.join(
            e for errs in form.errors.values() for e in errs
        ))
        return redirect('dashboard')


@login_required
def analyze(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            jd_text = form.cleaned_data['job_description']
            analysis = run_analysis(resume, jd_text)
            return redirect('results', analysis_id=analysis.id)
    else:
        form = JobDescriptionForm()

    return render(request, 'core/analyze.html', {'resume': resume, 'form': form})


def run_analysis(resume, jd_text):
    """Core pipeline: extract skills, score similarity, check ATS, build suggestions."""
    resume_text = resume.extracted_text or ''

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = sorted(set(resume_skills) & set(jd_skills))
    missing_skills = sorted(set(jd_skills) - set(resume_skills))

    similarity_score = compute_similarity_score(resume_text, jd_text)
    skill_overlap_score = compute_skill_overlap_score(matched_skills, jd_skills)

    page_count = count_pdf_pages(resume.file.path) if resume.file else 1
    ats_score, ats_issues = check_ats_compatibility(resume_text, page_count)

    overall_score = compute_overall_score(similarity_score, skill_overlap_score, ats_score)

    suggestions = generate_suggestions(missing_skills, similarity_score, ats_score, ats_issues)

    analysis = Analysis.objects.create(
        resume=resume,
        job_description=jd_text,
        similarity_score=similarity_score,
        ats_score=ats_score,
        overall_score=overall_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        ats_issues=ats_issues,
        suggestions=suggestions,
    )
    return analysis


@login_required
def results(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id, resume__user=request.user)
    return render(request, 'core/results.html', {'analysis': analysis})


@login_required
@require_POST
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    resume.file.delete(save=False)
    resume.delete()
    messages.success(request, 'Resume deleted.')
    return redirect('dashboard')
