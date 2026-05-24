from django.urls import path

from . import views

urlpatterns = [
    path('profile/setup', views.profile_setup, name='profile_setup'),
    path('profile/settings', views.profile_settings, name='profile_settings'),
    path('dentist/link', views.your_link, name='your_link'),
    path('dentist/<slug:public_slug>', views.public_consultation, name='public_consultation'),
]
