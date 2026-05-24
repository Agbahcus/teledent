from django import forms

from accounts.models import User

from .models import DentistProfile


class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = DentistProfile
        fields = ['license_number', 'specialty', 'state', 'lga', 'bio', 'consultation_fee']

        widgets = {
            'license_number': forms.TextInput(attrs={'placeholder': 'Your dental license number'}),
            'specialty': forms.Select(),
            'state': forms.Select(),
            'lga': forms.TextInput(attrs={'placeholder': 'e.g., Ikoyi, Lekki'}),
            'bio': forms.Textarea(
                attrs={'placeholder': 'Brief description of your practice and experience', 'rows': 4, 'maxlength': 200}
            ),
            'consultation_fee': forms.NumberInput(attrs={'placeholder': '5000'}),
        }

    STATE_CHOICES = [
        ('', 'Select a state'),
        ('Lagos', 'Lagos'),
        ('Abuja', 'Abuja'),
        ('Ibadan', 'Ibadan'),
        ('Benin City', 'Benin City'),
        ('Enugu', 'Enugu'),
        ('Kano', 'Kano'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['license_number'].required = True
        self.fields['specialty'].required = True
        self.fields['state'].required = True
        self.fields['consultation_fee'].required = True
        self.fields['state'].widget = forms.Select(choices=self.STATE_CHOICES)


class SettingsForm(forms.ModelForm):
    notify_sms = forms.BooleanField(required=False)
    notify_email = forms.BooleanField(required=False)

    class Meta:
        model = DentistProfile
        fields = ['response_time_hours']
        widgets = {'response_time_hours': forms.NumberInput(attrs={'min': 1})}


class ProfileEditForm(forms.ModelForm):
    STATE_CHOICES = ProfileSetupForm.STATE_CHOICES

    class Meta:
        model = DentistProfile
        fields = ['full_name', 'license_number', 'specialty', 'state', 'lga', 'bio', 'consultation_fee']
        widgets = {
            'full_name': forms.TextInput(),
            'license_number': forms.TextInput(),
            'specialty': forms.Select(),
            'state': forms.Select(),
            'lga': forms.TextInput(),
            'bio': forms.Textarea(attrs={'rows': 4, 'maxlength': 200}),
            'consultation_fee': forms.NumberInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].widget = forms.Select(choices=self.STATE_CHOICES)


class UserContactForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone']
        widgets = {'email': forms.EmailInput(), 'phone': forms.TextInput()}
