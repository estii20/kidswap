from django.shortcuts import render, redirect
from .models import ClothingItem
from .forms import UserRegisterForm
from django.contrib import messages

def home(request):
    items = ClothingItem.objects.filter(sold=False).order_by('-posted_at')
    return render(request, 'marketplace/home.html', {'items': items})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'marketplace/register.html', {'form': form})
