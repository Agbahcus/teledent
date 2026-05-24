import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class DentistProfile(models.Model):
    class Specialty(models.TextChoices):
        GENERAL = 'General', 'General Dentistry'
        ORTHO = 'Ortho', 'Orthodontics'
        PROSTHO = 'Prostho', 'Prosthodontics'
        PEDIATRIC = 'Pediatric', 'Pediatric Dentistry'
        ORAL_SURGERY = 'Oral Surgery', 'Oral Surgery'
        PERIO = 'Perio', 'Periodontics'
        ENDO = 'Endo', 'Endodontics'
        COSMETIC = 'Cosmetic', 'Cosmetic Dentistry'
        OTHER = 'Other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=150)
    specialty = models.CharField(max_length=50, choices=Specialty.choices, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    lga = models.CharField(max_length=100, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    consultation_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    response_time_hours = models.IntegerField(default=24)
    notify_sms = models.BooleanField(default=True)
    notify_email = models.BooleanField(default=True)
    average_rating = models.FloatField(default=0.0)
    total_consultations = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    public_slug = models.SlugField(max_length=200, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.public_slug and self.full_name:
            base = slugify(self.full_name)
            candidate = base or 'dentist'
            suffix = 1
            while DentistProfile.objects.filter(public_slug=candidate).exclude(pk=self.pk).exists():
                suffix += 1
                candidate = f'{base}-{suffix}'
            self.public_slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
