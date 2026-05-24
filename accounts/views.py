from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils import timezone

from dentist.models import DentistProfile

from .forms import LoginForm, RegisterForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                password=form.cleaned_data['password'],
            )
            DentistProfile.objects.create(user=user, full_name=form.cleaned_data['full_name'])
            login(request, user)
            return redirect('profile_setup')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(int(timedelta(days=30).total_seconds()))
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('landing')
    return redirect('dashboard' if request.user.is_authenticated else 'landing')

