import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm
from properties.models import Deal, Client

logger = logging.getLogger('users')


def register(request):
    if request.user.is_authenticated:
        return redirect('properties:home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = 'client'
        user.save()
        login(request, user)
        logger.info(f'New user registered: {user.username}')
        messages.success(request, f'Добро пожаловать, {user.first_name}!')
        return redirect('properties:home')
    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('properties:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        logger.info(f'User logged in: {user.username}')
        messages.success(request, f'Вы вошли как {user.username}.')
        return redirect(request.GET.get('next', 'properties:home'))
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    if request.user.is_authenticated:
        logger.info(f'User logged out: {request.user.username}')
    logout(request)
    return redirect('properties:home')


@login_required
def profile(request):
    user = request.user
    form = ProfileForm(request.POST or None, request.FILES or None, instance=user)
    deals = Deal.objects.none()
    try:
        if user.is_client():
            client = user.client_profile
            deals = Deal.objects.filter(client=client).select_related('property')[:5]
        elif user.is_employee():
            emp = user.employee_profile
            deals = Deal.objects.filter(agent=emp).select_related('property', 'client')[:5]
    except Exception:
        pass
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён.')
        return redirect('users:profile')
    return render(request, 'users/profile.html', {'form': form, 'deals': deals})
