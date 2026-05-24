from django import forms
from django.core.exceptions import ValidationError

from .models import Consultation


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class PublicConsultationForm(forms.ModelForm):
    DURATION_CHOICES = [
        ('', 'Select duration'),
        ('Less than 24 hours', 'Less than 24 hours'),
        ('1-3 days', '1-3 days'),
        ('4-7 days', '4-7 days'),
        ('More than 1 week', 'More than 1 week'),
    ]

    symptom_duration = forms.ChoiceField(choices=DURATION_CHOICES)

    class Meta:
        model = Consultation
        fields = [
            'patient_name',
            'patient_phone',
            'patient_email',
            'pain_level',
            'symptom_duration',
            'has_swelling',
            'has_bleeding',
            'has_fever',
            'has_trauma',
            'patient_complaint',
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'patient_phone': forms.TextInput(attrs={'placeholder': '08012345678'}),
            'patient_email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'pain_level': forms.NumberInput(attrs={'min': 0, 'max': 10}),
            'patient_complaint': forms.Textarea(attrs={'placeholder': 'Describe your dental concern', 'rows': 5}),
        }

    def clean_pain_level(self):
        value = self.cleaned_data['pain_level']
        if value < 0 or value > 10:
            raise ValidationError('Pain level must be between 0 and 10.')
        return value

    # Accept images via a file input (not stored on the Consultation model)
    images = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True}),
        help_text='Upload up to 3 photos. JPG/PNG/WEBP. Max 5MB each.',
    )

    def clean_images(self):
        images = self.files.getlist('images') if hasattr(self, 'files') else []
        errors = []
        allowed_content_types = {'image/jpeg', 'image/png', 'image/webp'}
        if len(images) > 3:
            raise ValidationError('Upload a maximum of 3 photos.')
        for image in images:
            if image.content_type not in allowed_content_types:
                raise ValidationError('Photos must be JPG, PNG, or WEBP files.')
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Each photo must be 5MB or smaller.')
        return images


class RespondForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            'dentist_diagnosis',
            'dentist_treatment_plan',
            'dentist_medications',
            'dentist_follow_up',
            'follow_up_due',
        ]
        widgets = {
            'dentist_diagnosis': forms.Textarea(
                attrs={'placeholder': "What did you diagnose based on the patient's complaint and photos?", 'rows': 5}
            ),
            'dentist_treatment_plan': forms.Textarea(
                attrs={
                    'placeholder': 'What treatment should the patient consider? Should they come in-person?',
                    'rows': 5,
                }
            ),
            'dentist_medications': forms.Textarea(
                attrs={'placeholder': 'Any medications you recommend? (e.g., Ibuprofen 400mg twice daily)', 'rows': 4}
            ),
            'dentist_follow_up': forms.Textarea(
                attrs={'placeholder': 'When should they return for follow-up? What should they watch for?', 'rows': 4}
            ),
            'follow_up_due': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_dentist_diagnosis(self):
        val = (self.cleaned_data.get('dentist_diagnosis') or '').strip()
        if len(val) < 10:
            raise ValidationError('Diagnosis must be at least 10 characters.')
        return val

    def clean_dentist_treatment_plan(self):
        val = (self.cleaned_data.get('dentist_treatment_plan') or '').strip()
        if len(val) < 10:
            raise ValidationError('Treatment plan must be at least 10 characters.')
        return val

    def clean_dentist_follow_up(self):
        val = (self.cleaned_data.get('dentist_follow_up') or '').strip()
        if len(val) < 10:
            raise ValidationError('Follow-up instructions must be at least 10 characters.')
        return val
