from django.shortcuts import render

def welcome(request):
    return render(request, 'frontsite/welcome.html')

def login(request):
    return render(request, 'frontsite/login.html')

def register(request):
    return render(request, 'frontsite/register.html')

def home(request):
    return render(request, 'frontsite/home.html')

def detail(request):
    return render(request, 'frontsite/detail.html')