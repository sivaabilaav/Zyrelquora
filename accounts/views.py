
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileForm


# User Registration
def register_view(request):

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('/accounts/login/')

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# User Login
def login_view(request):

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')

    else:
        form = AuthenticationForm()

    form.fields['username'].label = 'Email Address'

    return render(request, 'accounts/login.html', {'form': form})


# User Logout
def logout_view(request):

    logout(request)
    return redirect('/accounts/login/')


# Customer Profile
@login_required
def profile_view(request):

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')

    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form
    })
