from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import Stage, UserProfile, Team
from .forms import UserUpdateForm, ProfileUpdateForm


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


@csrf_protect
def register_user(request):
    if request.method == 'GET':
        teams = Team.objects.all()
        return render(request, 'registration/registration.html', {'teams': teams})

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        team_id = request.POST['team']
        new_team_name = request.POST['new_team']
        phone_number = request.POST['phone_number']
        address = request.POST['address']
        date_of_birth = request.POST['date_of_birth']
        city = request.POST['city']
        gender = request.POST['gender']
        country = request.POST['country']

        errors = []

        if password != password2:
            errors.append('Slaptažodžiai nesutampa.')
        if User.objects.filter(username=username).exists():
            errors.append(f'Vartotojo vardas {username} užimtas.')
        if not email:
            errors.append('El. paštas yra privalomas.')
        if User.objects.filter(email=email).exists():
            errors.append(f'El. paštas {email} jau registruotas.')
        if '@' in username:
            errors.append('Vartotojo vardas negali turėti simbolio "@"')

        if errors:
            for error in errors:
                messages.warning(request, error)
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                        last_name=last_name)
        user.save()

        # Sukurkite arba gaukite komandą
        team = None
        if new_team_name:
            team, created = Team.objects.get_or_create(name=new_team_name)
        elif team_id:
            team = get_object_or_404(Team, id=team_id)

        # Atnaujinkite UserProfile su papildomais laukais
        user.userprofile.team = team
        user.userprofile.phone_number = phone_number
        user.userprofile.address = address
        user.userprofile.date_of_birth = date_of_birth
        user.userprofile.city = city
        user.userprofile.gender = gender
        user.userprofile.country = country
        user.userprofile.save()

        messages.success(request, 'Jūsų registracija sėkminga!')
        return redirect('login')


@login_required
def profile(request):
    user_profile = request.user.userprofile
    context = {
        'user': request.user,
        'profile': user_profile
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profilis atnaujintas sėkmingai!')
            return redirect('profile')
        else:
            messages.warning(request, 'Profilis neatnaujintas, prašome patikrinti formą.')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'edit_profile.html', context)
