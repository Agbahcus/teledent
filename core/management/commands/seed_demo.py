from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from consultations.models import Consultation
from dentist.models import DentistProfile


class Command(BaseCommand):
    help = 'Create a demo dentist user and sample consultations'

    def handle(self, *args, **options):
        email = 'demo@clinic.com'
        password = 'demo12345'

        user, created = User.objects.get_or_create(email=email, defaults={'phone': '08012345678'})
        if created:
            user.set_password(password)
            user.save()

        profile, _ = DentistProfile.objects.get_or_create(user=user, defaults={'full_name': 'Dr. Demo Dentist'})
        profile.specialty = profile.specialty or DentistProfile.Specialty.GENERAL
        profile.state = profile.state or 'Lagos'
        profile.consultation_fee = profile.consultation_fee or 5000
        profile.save()

        if not Consultation.objects.filter(dentist=profile).exists():
            Consultation.objects.create(
                dentist=profile,
                patient_name='Aisha Bello',
                patient_phone='08011112222',
                patient_email='aisha@example.com',
                patient_complaint='Severe toothache on lower right molar for 2 days.',
                status=Consultation.Status.NEW,
            )
            Consultation.objects.create(
                dentist=profile,
                patient_name='Tunde Ade',
                patient_phone='08033334444',
                patient_email='tunde@example.com',
                patient_complaint='Gum swelling and bleeding after brushing.',
                status=Consultation.Status.IN_REVIEW,
            )
            Consultation.objects.create(
                dentist=profile,
                patient_name='Ngozi Okafor',
                patient_phone='08055556666',
                patient_email='ngozi@example.com',
                patient_complaint='Sensitive teeth when drinking cold water.',
                status=Consultation.Status.RESPONDED,
                dentist_diagnosis='Based on the complaint, likely dentin hypersensitivity.',
                dentist_treatment_plan='Use desensitizing toothpaste and schedule an in-clinic evaluation.',
                dentist_medications='None prescribed',
                dentist_follow_up='If pain persists after 7 days, visit the clinic for assessment.',
                dentist_response_date=timezone.now(),
            )

        self.stdout.write(self.style.SUCCESS('Demo data ready. Login: demo@clinic.com / demo12345'))

