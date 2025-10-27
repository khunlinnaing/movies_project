from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from project.collectForms.login_form import LoginForm
# Create your views here.
def index(request):
    return render(request, 'base/body.html')

def login_view(request):
    form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def login_view_post(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = request.POST.get('username')
            password = request.POST.get('password')
            if '@' in username_or_email:
                try:
                    user = User.objects.get(email=username_or_email)
                    username = user.username
                except User.DoesNotExist:
                    messages.error(request, 'No account found with that email.')
                    return redirect('website:login-view-get')
            else:
                username = username_or_email
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('website:index-view')
            else:
                messages.error(request, 'Invalid username/email or password.')
                return redirect('website:login-view-get')
        else:
            messages.error(request, 'Invalid username/email or password.')
            return redirect('website:login-view-get')