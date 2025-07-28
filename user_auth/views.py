from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm

# Create your views here.

def signup_view(request):
    """View for user registration."""
    if request.user.is_authenticated:
        return redirect('document_analyzer:index')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('document_analyzer:index')
    else:
        form = SignUpForm()
    
    return render(request, 'user_auth/signup.html', {'form': form})

def login_view(request):
    """View for user login."""
    if request.user.is_authenticated:
        return redirect('document_analyzer:index')
        
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                # Redirect to the page the user was trying to access, or home
                next_page = request.GET.get('next', 'document_analyzer:index')
                return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'user_auth/login.html', {'form': form})

@login_required
def logout_view(request):
    """View for user logout."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('document_analyzer:index')
