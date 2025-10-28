from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from project.collectForms.login_form import LoginForm


def index(request):
    """
    Home page view.
    """
    return render(request, 'base/body.html')


def login_view(request):
    """
    Display the login page with the login form.
    """
    form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def login_view_post(request):
    """
    Handle login form submission.
    Supports username or email authentication.
    """
    if request.method != "POST":
        return redirect('website:login-view-get')

    form = LoginForm(request, data=request.POST)

    if not form.is_valid():
        messages.error(request, 'Invalid username/email or password.')
        return redirect('website:login-view-get')

    username_or_email = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password')

    user = authenticate(request, username=username_or_email, password=password)

    if user is not None:
        login(request, user)
        return redirect('website:index-view')

    messages.error(request, "Invalid username/email or password.")
    return redirect('website:login-view-get')
