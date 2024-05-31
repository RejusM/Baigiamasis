from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from .models import Stage, Team, RaceRegistration, Track, RaceResult, OverallTeamScore, OverallUserScore
from .forms import UserUpdateForm, ProfileUpdateForm, RaceResultForm


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
    registrations = RaceRegistration.objects.filter(stage=stage, status='p')
    context = {
        'stage': stage,
        'registrations': registrations,
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

        team = None
        if new_team_name:
            team, created = Team.objects.get_or_create(name=new_team_name)
        elif team_id:
            team = get_object_or_404(Team, id=team_id)

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


@login_required
def registration_list(request):
    stages = Stage.objects.all()
    stage_registrations = {
        stage: RaceRegistration.objects.filter(stage=stage) for stage in stages
    }
    context = {
        'stage_registrations': stage_registrations,
    }
    return render(request, 'race_registration/registration_list.html', context)


@staff_member_required
def review_registration(request, registration_id):
    registration = get_object_or_404(RaceRegistration, id=registration_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        comments = request.POST.get('comments')
        registration.status = status
        registration.comments = comments
        registration.save()
        messages.success(request, 'Registracijos būsena atnaujinta sėkmingai!')
        return redirect('registration_list')

    context = {
        'registration': registration,
    }
    return render(request, 'race_registration/review_registration.html', context)


@login_required
def register_for_race(request):
    stage_id = request.GET.get('stage_id')
    stages = Stage.objects.all()
    tracks = Track.objects.filter(stages__id=stage_id) if stage_id else Track.objects.none()

    if request.method == 'POST':
        stage_id = request.POST['stage_id']
        track_id = request.POST['track']
        stage = get_object_or_404(Stage, id=stage_id)
        track = get_object_or_404(Track, id=track_id)
        user_profile = request.user.userprofile

        # Patikrinkite, ar vartotojas jau užsiregistravo į šį etapą ir trasą
        if RaceRegistration.objects.filter(user_profile=user_profile, stage=stage, track=track).exists():
            messages.warning(request, 'Jūs jau esate užsiregistravę į šią trasą šiame etape.')
        else:
            registration = RaceRegistration(user_profile=user_profile, stage=stage, track=track)
            registration.save()
            messages.success(request, 'Jūs sėkmingai užsiregistravote į etapą!')
            return redirect('registration_list')

    return render(request, 'race_registration/register_for_race.html',
                  {'stages': stages, 'tracks': tracks, 'selected_stage_id': stage_id})


def participants_list(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)
    registrations = RaceRegistration.objects.filter(stage=stage)
    return render(request, 'race_registration/participants_list.html', {'stage': stage, 'registrations': registrations})


@staff_member_required
def add_race_result(request):
    stage_id = request.GET.get('stage_id')
    if request.method == 'POST':
        form = RaceResultForm(request.POST, stage_id=stage_id)
        if form.is_valid():
            race_result = form.save(commit=False)
            race_result.user_profile = form.cleaned_data['user']
            race_result.stage_id = stage_id
            race_result.save()
            messages.success(request, 'Rezultatas sėkmingai pridėtas.')
            return redirect('race_result_list')
        else:
            messages.error(request, 'Klaida pridedant rezultatą. Patikrinkite įvestus duomenis.')
    else:
        form = RaceResultForm(stage_id=stage_id)
    return render(request, 'result/add_race_result.html', {'form': form, 'stage_id': stage_id})


def race_result_list(request):
    stages = Stage.objects.all()
    return render(request, 'result/race_result_list.html', {'stages': stages})


@staff_member_required
def edit_race_result(request, result_id):
    result = get_object_or_404(RaceResult, id=result_id)
    stage_id = result.stage.id
    if request.method == 'POST':
        form = RaceResultForm(request.POST, instance=result, stage_id=stage_id)
        if form.is_valid():
            race_result = form.save(commit=False)
            race_result.user_profile = form.cleaned_data['user']
            race_result.save()
            messages.success(request, 'Rezultatas sėkmingai atnaujintas.')
            return redirect('race_result_list')
    else:
        form = RaceResultForm(instance=result, stage_id=stage_id)
        form.fields['user'].initial = result.user_profile
    return render(request, 'result/edit_race_result.html', {'form': form, 'result': result})


def personal_results(request):
    user_profile = request.user.userprofile
    results = RaceResult.objects.filter(user_profile=user_profile).order_by('stage__date')
    total_points = results.aggregate(Sum('points'))['points__sum'] or 0
    return render(request, 'result/personal_results.html', {
        'results': results,
        'total_points': total_points,
    })


def team_results(request):
    if not request.user.userprofile.team:
        messages.error(request, 'Jūs nepriklausote komandai.')
        return redirect('home')

    team = request.user.userprofile.team
    results = RaceResult.objects.filter(user_profile__team=team).order_by('stage__date')
    team_scores = results.values('stage__name').annotate(total_points=Sum('points')).order_by('stage__date')
    return render(request, 'result/team_results.html', {
        'team': team,
        'results': results,
        'team_scores': team_scores,
    })


def overall_user_scores(request):
    user_scores = OverallUserScore.objects.all().order_by('-total_points')
    return render(request, 'result/overall_user_scores.html', {
        'user_scores': user_scores,
    })


def overall_team_scores(request):
    team_scores = OverallTeamScore.objects.all().order_by('-total_points')
    return render(request, 'result/overall_team_scores.html', {
        'team_scores': team_scores,
    })
