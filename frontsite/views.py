from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from frontsite.models import Profile


def welcome(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'frontsite/welcome.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang kembali, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Username atau password salah')
            return redirect('login')

    return render(request, 'frontsite/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')  # ⬅ ambil email
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Password tidak cocok')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan')
            return redirect('register')

        # ⬇ tambahkan email saat create_user
        User.objects.create_user(username=username, password=password1, email=email)

        messages.success(request, 'Akun berhasil dibuat! Silakan login.')
        return redirect('login')

    return render(request, 'frontsite/register.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Berhasil logout.')
    return redirect('login')


@login_required(login_url='login')
def home(request):
    return render(request, 'frontsite/home.html')


@login_required(login_url='login')
def about(request):
    return render(request, 'frontsite/about.html')

@login_required
def profile_setting(request):
    user = request.user
    return render(request, 'frontsite/settings.html', {
        'user': user
    })

@login_required
def update_profile(request):
    user = request.user

    # pastikan profil user ada
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')

        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email

        if request.FILES.get('photo'):
            profile.foto = request.FILES['photo']
            profile.save()

        user.save()
        messages.success(request, 'Data berhasil disimpan.')

    return redirect('profile_setting')