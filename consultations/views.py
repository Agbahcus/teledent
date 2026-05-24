from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from dentist.models import DentistProfile

from .forms import RespondForm
from .models import Consultation, ResponseTemplate


def _dentist_profile(request):
    return DentistProfile.objects.get(user=request.user)


@login_required
def dashboard(request):
    profile = _dentist_profile(request)
    qs = Consultation.objects.filter(dentist=profile).order_by('-created_at')

    status_filter = (request.GET.get('status') or 'ALL').upper()
    if status_filter in {'NEW', 'IN_REVIEW', 'RESPONDED', 'RESOLVED'}:
        qs = qs.filter(status=status_filter)

    counts = Consultation.objects.filter(dentist=profile).values('status').annotate(c=Count('id'))
    counts_map = {row['status']: row['c'] for row in counts}
    avg_rating = Consultation.objects.filter(dentist=profile, rating__isnull=False).aggregate(v=Avg('rating'))['v'] or 0
    urgent_count = Consultation.objects.filter(dentist=profile, urgency='URGENT').exclude(status='RESOLVED').count()
    follow_up_count = Consultation.objects.filter(
        dentist=profile,
        follow_up_due__isnull=False,
    ).exclude(status='RESOLVED').count()

    context = {
        'profile': profile,
        'consultations': qs,
        'status_filter': status_filter,
        'counts': {
            'NEW': counts_map.get('NEW', 0),
            'IN_REVIEW': counts_map.get('IN_REVIEW', 0),
            'RESPONDED': counts_map.get('RESPONDED', 0),
        },
        'avg_rating': round(float(avg_rating), 1) if avg_rating else 0,
        'urgent_count': urgent_count,
        'follow_up_count': follow_up_count,
    }
    return render(request, 'dashboard.html', context)


@login_required
def consultations_list(request):
    return redirect('dashboard')


@login_required
def view_consultation(request, consultation_id):
    profile = _dentist_profile(request)
    consultation = get_object_or_404(Consultation, id=consultation_id, dentist=profile)
    return render(request, 'view_consultation.html', {'profile': profile, 'consultation': consultation})


@login_required
def respond_consultation(request, consultation_id):
    profile = _dentist_profile(request)
    consultation = get_object_or_404(Consultation, id=consultation_id, dentist=profile)
    templates = _ensure_response_templates(profile)

    if request.method == 'POST':
        form = RespondForm(request.POST, instance=consultation)
        if form.is_valid():
            c = form.save(commit=False)
            c.status = Consultation.Status.RESPONDED
            c.dentist_response_date = timezone.now()
            c.save()
            messages.success(request, 'Response submitted! Patient will be notified.')
            return redirect('dashboard')
    else:
        form = RespondForm(instance=consultation)

    return render(
        request,
        'respond_consultation.html',
        {'profile': profile, 'consultation': consultation, 'form': form, 'templates': templates},
    )


def _ensure_response_templates(profile):
    if profile.response_templates.exists():
        return profile.response_templates.all()

    defaults = [
        {
            'title': 'Toothache',
            'diagnosis': 'The symptoms suggest tooth pain that needs clinical evaluation to identify the exact cause.',
            'treatment_plan': 'Use warm salt-water rinses and avoid chewing on the affected side. Please schedule an in-person dental assessment as soon as possible.',
            'medications': 'Ibuprofen or paracetamol may help if you can safely take them. Avoid antibiotics unless prescribed after assessment.',
            'follow_up': 'If pain worsens, swelling develops, or fever starts, seek urgent in-person care immediately.',
        },
        {
            'title': 'Gum Swelling',
            'diagnosis': 'The symptoms suggest gum inflammation or possible infection around the affected area.',
            'treatment_plan': 'Keep the area clean, rinse gently with warm salt water, and book an in-person examination to check for infection or trapped debris.',
            'medications': 'Pain relief may be used if safe for you. Antibiotics require clinical confirmation.',
            'follow_up': 'Follow up within 48 hours, or immediately if swelling spreads or fever occurs.',
        },
        {
            'title': 'Sensitivity',
            'diagnosis': 'The symptoms may be consistent with tooth sensitivity, gum recession, enamel wear, or early decay.',
            'treatment_plan': 'Use desensitizing toothpaste twice daily and avoid very cold, acidic, or sugary foods until assessed.',
            'medications': '',
            'follow_up': 'If sensitivity persists beyond one week or becomes spontaneous pain, schedule an in-person visit.',
        },
    ]
    ResponseTemplate.objects.bulk_create([ResponseTemplate(dentist=profile, **item) for item in defaults])
    return profile.response_templates.all()


@login_required
def mark_reviewing(request, consultation_id):
    if request.method != 'POST':
        return redirect('view_consultation', consultation_id=consultation_id)
    profile = _dentist_profile(request)
    consultation = get_object_or_404(Consultation, id=consultation_id, dentist=profile)
    consultation.mark_in_review()
    messages.success(request, 'Marked as in review.')
    return redirect('view_consultation', consultation_id=consultation_id)


@login_required
def mark_resolved(request, consultation_id):
    if request.method != 'POST':
        return redirect('view_consultation', consultation_id=consultation_id)
    profile = _dentist_profile(request)
    consultation = get_object_or_404(Consultation, id=consultation_id, dentist=profile)
    consultation.mark_resolved()
    messages.success(request, 'Marked as resolved.')
    return redirect('view_consultation', consultation_id=consultation_id)
