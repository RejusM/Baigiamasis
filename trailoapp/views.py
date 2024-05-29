from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Stage, UserProfile, Team


def home(request):
    stages = Stage.objects.all().order_by('date')
    stages_count = stages.count()
    context = {
        'stages': stages,
        'stages_count': stages_count,
    }
    return render(request, 'home.html', context)


def all_stages(request):
    stages = Stage.objects.all().order_by('date')
    context = {
        'stages': stages
    }
    return render(request, 'all_stages.html', context)


def stage_detail(request, id):
    stage = get_object_or_404(Stage, id=id)
    context = {
        'stage': stage,
    }
    return render(request, 'stage_detail.html', context)


def register(request):
    teams = Team.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        team_id = request.POST.get('team')
        new_team_name = request.POST.get('new_team')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')
        city = request.POST.get('city')
        gender = request.POST.get('gender')
        country = request.POST.get('country')

        if password != password2:
            messages.error(request, 'Slaptažodžiai nesutampa.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Vartotojo vardas jau egzistuoja.')
            return redirect('register')

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name,
                                        last_name=last_name)
        user.save()

        team = None
        if new_team_name:
            team, created = Team.objects.get_or_create(name=new_team_name)
        elif team_id:
            team = get_object_or_404(Team, id=team_id)

        user_profile = UserProfile(user=user, team=team, phone_number=phone_number, address=address,
                                   date_of_birth=date_of_birth, city=city, gender=gender, country=country)
        user_profile.save()

        login(request, user)
        messages.success(request, 'Registracija sėkminga!')
        return redirect('home')

    return render(request, 'registration/register.html', {'teams': teams})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Sveiki sugrįžę, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Neteisingi prisijungimo duomenys')
            return redirect('login')
    return render(request, 'registration/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'Jūs sėkmingai atsijungėte.')
    return redirect('home')
