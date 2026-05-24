import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from dentist.models import DentistProfile


class Consultation(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'NEW'
        IN_REVIEW = 'IN_REVIEW', 'IN REVIEW'
        RESPONDED = 'RESPONDED', 'RESPONDED'
        RESOLVED = 'RESOLVED', 'RESOLVED'

    class Urgency(models.TextChoices):
        URGENT = 'URGENT', 'URGENT'
        PRIORITY = 'PRIORITY', 'PRIORITY'
        ROUTINE = 'ROUTINE', 'ROUTINE'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name='consultations')

    patient_name = models.CharField(max_length=150)
    patient_phone = models.CharField(max_length=30)
    patient_email = models.EmailField()
    patient_complaint = models.TextField()
    pain_level = models.IntegerField(default=0)
    symptom_duration = models.CharField(max_length=50, blank=True)
    has_swelling = models.BooleanField(default=False)
    has_bleeding = models.BooleanField(default=False)
    has_fever = models.BooleanField(default=False)
    has_trauma = models.BooleanField(default=False)
    urgency = models.CharField(max_length=20, choices=Urgency.choices, default=Urgency.ROUTINE)
    triage_summary = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    dentist_diagnosis = models.TextField(null=True, blank=True)
    dentist_treatment_plan = models.TextField(null=True, blank=True)
    dentist_medications = models.TextField(null=True, blank=True)
    dentist_follow_up = models.TextField(null=True, blank=True)
    follow_up_due = models.DateField(null=True, blank=True)
    dentist_response_date = models.DateTimeField(null=True, blank=True)

    rating = models.IntegerField(null=True, blank=True)
    rating_comment = models.CharField(max_length=300, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def score_urgency(self):
        if self.has_fever or self.has_trauma or (self.has_swelling and self.pain_level >= 7):
            return self.Urgency.URGENT
        if self.pain_level >= 5 or self.has_swelling or self.has_bleeding:
            return self.Urgency.PRIORITY
        return self.Urgency.ROUTINE

    def build_triage_summary(self):
        symptoms = []
        if self.has_swelling:
            symptoms.append('swelling')
        if self.has_bleeding:
            symptoms.append('bleeding')
        if self.has_fever:
            symptoms.append('fever')
        if self.has_trauma:
            symptoms.append('trauma')
        symptom_text = ', '.join(symptoms) if symptoms else 'no red-flag symptoms selected'
        duration = self.symptom_duration or 'duration not specified'
        return f'Pain {self.pain_level}/10, {duration}, {symptom_text}.'

    def save(self, *args, **kwargs):
        self.urgency = self.score_urgency()
        self.triage_summary = self.build_triage_summary()
        super().save(*args, **kwargs)

    def mark_in_review(self):
        if self.status == self.Status.NEW:
            self.status = self.Status.IN_REVIEW
            # Recalculate urgency/triage in save(); include them in update_fields
            self.save(update_fields=['status', 'urgency', 'triage_summary'])

    def mark_resolved(self):
        self.status = self.Status.RESOLVED
        self.resolved_at = timezone.now()
        # Ensure urgency and triage_summary are saved when resolving
        self.save(update_fields=['status', 'resolved_at', 'urgency', 'triage_summary'])

    def __str__(self):
        return f'{self.patient_name} ({self.status})'


class ResponseTemplate(models.Model):
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name='response_templates')
    title = models.CharField(max_length=100)
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    medications = models.TextField(blank=True)
    follow_up = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class ConsultationImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to='consultation_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Logic to prevent more than 3 images per consultation
        if not self.pk:
            if self.consultation.images.count() >= 3:
                raise ValidationError('A maximum of 3 images is allowed per consultation.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
