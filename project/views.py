from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from project.collectForms.login_form import LoginForm
from project.collectForms.signup_forms import SignupForm
from project.collectForms.categories_forms import CategoryForm
from project.models import Category

def index(request):
    """
    Home page view.
    """
    return render(request, 'base/body.html')


def login_view(request):
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
    try:
        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            login(request, user)
            return redirect('website:index-view')
        
    except Exception as e:
        messages.error(request, 'Server error')
        return redirect('website:login-view-get')

@login_required
def logout_view(request):
    logout(request)
    return redirect('website:index-view')

def signup_view(request):
    """
    Handles user registration (account + profile info).
    """
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('website:login-view-get')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = SignupForm()

    return render(request, 'auth/register.html', {'form': form})

@user_passes_test(lambda user: user.is_superuser)
@login_required
def category_view(request):
    categories= Category.objects.all().order_by('id')
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard/category/lists.html', {"category_objects": page_obj})

@user_passes_test(lambda user: user.is_superuser)
@login_required
def create_category_view(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Create category is success')
            return redirect('website:category-view')
    else:
        form = CategoryForm()
    
    return render(request, 'dashboard/category/add.html',{"form": form})

@user_passes_test(lambda user: user.is_superuser)
@login_required
def edit_category_view(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        if request.method == 'POST':
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'Update is success')
                return redirect('website:category-view')
            return render(request, 'dashboard/category/edit.html', {'form': form})
        else:
            form = CategoryForm(instance=category)
        return render(request, 'dashboard/category/edit.html', {'form': form})

    except Category.DoesNotExist:
        messages.error(request, 'Category id is not found.')
        return redirect('website:category-view')
    except Exception as e:
        messages.error(request, 'Server error')
        return redirect('website:category-view')


@user_passes_test(lambda user: user.is_superuser)
@login_required
def delete_category_view(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        category.delete()
        messages.success(request, 'Delete is success')
        return redirect('website:category-view')

    except Category.DoesNotExist:
        messages.error(request, 'Category id is not found.')
        return redirect('website:category-view')

    except Exception:
        # Any other server errors
        messages.error(request, 'Server error')
        return redirect('website:category-view')