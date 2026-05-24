import base64
from io import BytesIO

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from consultations.forms import PublicConsultationForm
from consultations.models import ConsultationImage

from .forms import ProfileEditForm, ProfileSetupForm, SettingsForm, UserContactForm
from .models import DentistProfile


@login_required
def profile_setup(request):
    profile = DentistProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile saved successfully.')
            return redirect('dashboard')
    else:
        form = ProfileSetupForm(instance=profile)

    return render(request, 'profile_setup.html', {'form': form, 'profile': profile})


@login_required
def profile_settings(request):
    profile = DentistProfile.objects.get(user=request.user)
    tab = (request.GET.get('tab') or 'profile').lower()

    profile_form = ProfileEditForm(instance=profile)
    user_form = UserContactForm(instance=request.user)
    settings_form = SettingsForm(
        instance=profile,
        initial={'notify_sms': profile.notify_sms, 'notify_email': profile.notify_email},
    )

    if request.method == 'POST':
        if tab == 'settings':
            settings_form = SettingsForm(request.POST, instance=profile)
            if settings_form.is_valid():
                profile.response_time_hours = settings_form.cleaned_data['response_time_hours']
                profile.notify_sms = settings_form.cleaned_data.get('notify_sms', False)
                profile.notify_email = settings_form.cleaned_data.get('notify_email', False)
                profile.save()
                messages.success(request, 'Settings updated successfully.')
                return redirect(f'{request.path}?tab=settings')
        else:
            profile_form = ProfileEditForm(request.POST, instance=profile)
            user_form = UserContactForm(request.POST, instance=request.user)
            ok = profile_form.is_valid() and user_form.is_valid()
            if ok:
                profile_form.save()
                user_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect(f'{request.path}?tab=profile')

    return render(
        request,
        'profile_settings.html',
        {'profile': profile, 'tab': tab, 'profile_form': profile_form, 'user_form': user_form, 'settings_form': settings_form},
    )


@login_required
def your_link(request):
    profile = DentistProfile.objects.get(user=request.user)
    public_url = request.build_absolute_uri(f'/dentist/{profile.public_slug}')

    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(public_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#1f2937', back_color='#ffffff')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_b64 = base64.b64encode(buffer.getvalue()).decode('ascii')

    return render(
        request,
        'your_link.html',
        {'profile': profile, 'public_url': public_url, 'qr_data_url': f'data:image/png;base64,{qr_b64}'},
    )


def public_consultation(request, public_slug):
    profile = get_object_or_404(DentistProfile, public_slug=public_slug)

    if request.method == 'POST':
        form = PublicConsultationForm(request.POST, request.FILES)
        image_errors = []
        if form.is_valid():
            images = form.cleaned_data.get('images') or []
            consultation = form.save(commit=False)
            consultation.dentist = profile
            consultation.save()
            for image in images:
                ConsultationImage.objects.create(consultation=consultation, image_file=image)
            messages.success(request, 'Consultation submitted successfully.')
            return redirect('public_consultation', public_slug=profile.public_slug)
        else:
            # collect image-related errors if any
            try:
                form.clean_images()
            except ValidationError as e:
                image_errors = e.messages
    else:
        form = PublicConsultationForm()
        image_errors = []

    return render(request, 'public_consultation.html', {'profile': profile, 'form': form, 'image_errors': image_errors})


def _validate_consultation_images(images):
    errors = []
    allowed_content_types = {'image/jpeg', 'image/png', 'image/webp'}
    if len(images) > 3:
        errors.append('Upload a maximum of 3 photos.')
    for image in images:
        if image.content_type not in allowed_content_types:
            errors.append('Photos must be JPG, PNG, or WEBP files.')
            break
        if image.size > 5 * 1024 * 1024:
            errors.append('Each photo must be 5MB or smaller.')
            break
    return errors
