# authentication/views.py

from django.shortcuts import render, redirect
# Import authenticate, login, logout from here
from django.contrib.auth import authenticate, login, logout
# Import the form that was missing
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_page = request.GET.get('next')
            return redirect(next_page) if next_page else redirect('catalog:product-list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'authentication/login.html')

def logout_view(request):
    logout(request)
    return redirect('auth:login')

# Your register_view will now work correctly
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('catalog:product-list')
    else:
        form = UserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})