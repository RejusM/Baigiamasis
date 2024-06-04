from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Stage, Team, RaceRegistration, Track, RaceResult, OverallTeamScore, OverallUserScore, UserProfile
from .forms import UserUpdateForm, ProfileUpdateForm, RaceResultForm, TrackForm, StageForm


def home(request):
    """
    Rodo pradinį puslapį su būsimais ir praėjusiais etapais
    :param request:
    :return:
    """
    now = timezone.now()
    upcoming_stages = Stage.objects.filter(date__gte=now).order_by('date')
    past_stages = Stage.objects.filter(date__lt=now).order_by('-date')
    context = {
        'upcoming_stages': upcoming_stages,
        'past_stages': past_stages,
    }
    return render(request, 'home.html', context)


def all_stages(request):
    stages = Stage.objects.all()
    now = timezone.now()
    return render(request, 'all_stages.html', {'stages': stages, 'now': now})


def stage_detail(request, id):
    """
    Rodo detalią informacija apie pasirinkta etapą ir patvirtintas registracijas
    :param request:
    :param id:
    :return:
    """
    stage = get_object_or_404(Stage, id=id)
    registrations = RaceRegistration.objects.filter(stage=stage, status='p')
    context = {
        'stage': stage,
        'registrations': registrations,
    }
    return render(request, 'stage_detail.html', context)


@csrf_protect
def register_user(request):
    """
   Registracija sistemoje
    :param request:
    :return:
    """
    if request.method == 'GET':
        # Grąžinama registracijos forma su visomis galimomis komandomis
        teams = Team.objects.all()
        return render(request, 'registration/registration.html', {'teams': teams})

    if request.method == 'POST':
        # Registracijos duomenų ištraukimas iš POST užklausos
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

        # Klaidų sąrašas
        errors = []

        # Registracijos duomenų tikrinimas
        if password != password2:
            errors.append('Slaptažodžiai nesutampa.')
        if User.objects.filter(username=username).exists():
            errors.append(f'Vartotojo vardas {username} užimtas.')
        if not email:
            errors.append('El. paštas yra privalomas.')
        if User.objects.filter(email=email).exists():
            errors.append(f'El. paštas {email} jau registruotas.')
        if '@' in username:
            errors.append('Vartotojo vardas negali turėti simbolio "@".')

        # Jei yra klaidų, grąžinama atgal į registracijos formą su klaidų pranešimais.
        if errors:
            for error in errors:
                messages.warning(request, error)
            return redirect('register')

        # Naudotojo sukurimas, jei visi duomenys teisingi.
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                        last_name=last_name)
        user.save()

        # Naudotojo profilio sukurimas arba komandos priskyrimas, jei yra nurodyta.
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

        # Registracijos sėkmės pranešimas ir nukreipimas į prisijungimo puslapį.
        messages.success(request, 'Jūsų registracija sėkminga!')
        return redirect('login')


@login_required
def profile(request):
    user_profile = request.user.userprofile
    registrations = RaceRegistration.objects.filter(user_profile=user_profile)

    for registration in registrations:
        if timezone.now() > registration.stage.registration_end:
            registration.status = 'Registracija baigėsi'
        else:
            registration.status = 'Registracija galima'

    return render(request, 'profile.html', {'registrations': registrations})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Jūsų profilis buvo atnaujintas!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)

    teams = Team.objects.all()  # Gauti visas komandas

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'teams': teams  # Perduoti komandas šablonui
    }

    return render(request, 'edit_profile.html', context)


@staff_member_required
def review_registrations(request, stage_id):
    """
    Leidžia adminui peržiūrėti ir atnaujinti visų paraiškų statusą pagal etapą
    :param request:
    :param stage_id:
    :return:
    """
    stage = get_object_or_404(Stage, id=stage_id)
    registrations = RaceRegistration.objects.filter(stage=stage)

    if request.method == "POST":
        registration_id = request.POST.get("registration_id")
        registration = get_object_or_404(RaceRegistration, id=registration_id)
        status = request.POST.get("status")

        if status == "Atmesta":
            registration.delete()
            messages.success(request, "Paraiška atmesta ir ištrinta sėkmingai!")
        else:
            registration.status = status
            registration.save()
            messages.success(request, "Paraiška atnaujinta sėkmingai!")

        return redirect("review_registrations", stage_id=stage.id)

    for registration in registrations:
        registration.full_name = f"{registration.user_profile.user.first_name} {registration.user_profile.user.last_name}"

    return render(request, 'race_registration/review_registrations.html',
                  {'stage': stage, 'registrations': registrations})


@login_required
def register_for_race(request):
    """
    Registracija į etapus
    :param request:
    :return:
    """
    now = timezone.now()
    stages = Stage.objects.filter(registration_end__gt=now)

    stage_id = request.GET.get('stage_id')
    selected_stage = get_object_or_404(Stage, id=stage_id) if stage_id else None
    tracks = Track.objects.filter(stages__id=stage_id) if stage_id else Track.objects.none()

    if request.method == 'POST' and selected_stage:
        user_profile = request.user.userprofile
        track_id = request.POST['track']
        track = get_object_or_404(Track, id=track_id)

        existing_registration = RaceRegistration.objects.filter(user_profile=user_profile, stage=selected_stage)
        if existing_registration.exists():
            registered_track = existing_registration.first().track
            messages.warning(request, f'Jūs jau esate užsiregistravęs į trasą "{registered_track.name}" šiame etape.')
            return redirect('participants_list', stage_id=selected_stage.id)
        else:
            registration = RaceRegistration(user_profile=user_profile, stage=selected_stage, track=track)
            registration.save()
            messages.success(request, 'Jūs sėkmingai užsiregistravote į etapą!')
            return redirect('participants_list', stage_id=selected_stage.id)

    return render(request, 'race_registration/register_for_race.html', {
        'stages': stages,
        'tracks': tracks,
        'selected_stage_id': stage_id,
        'selected_stage': selected_stage,
        'now': now
    })


def participants_list(request, stage_id):
    """
    Rodo sąrašą dalyvių, kurie užsiregistravę į konkretų etapą
    :param request:
    :param stage_id:
    :return:
    """
    stage = get_object_or_404(Stage, id=stage_id)
    registrations = RaceRegistration.objects.filter(stage=stage)
    return render(request, 'race_registration/participants_list.html', {'stage': stage, 'registrations': registrations})


@staff_member_required
def add_race_result(request):
    """
    Leidžia pridėti naujus varžybų rezultatus
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = RaceResultForm(request.POST)
        if form.is_valid():
            race_result = form.save(commit=False)
            race_result.user_profile = form.cleaned_data['user']
            race_result.save()
            messages.success(request, 'Rezultatas sėkmingai pridėtas.')
            return redirect('race_result_list')
        else:
            messages.error(request, 'Klaida pridedant rezultatą. Patikrinkite įvestus duomenis.')
    else:
        form = RaceResultForm()

    return render(request, 'result/add_race_result.html', {'form': form})


def race_result_list(request):
    """
    Rodo visus varžybų rezultatus pagal pasirinktą etapą ir trasą
    :param request:
    :return:
    """
    stages = Stage.objects.all()
    selected_stage_id = request.GET.get('stage_id')
    selected_track_id = request.GET.get('track_id')
    selected_stage = None
    selected_track = None
    results = None

    if selected_stage_id:
        selected_stage = get_object_or_404(Stage, id=selected_stage_id)
        tracks = selected_stage.tracks.all()

        if selected_track_id:
            selected_track = get_object_or_404(Track, id=selected_track_id, stages=selected_stage)
            results = RaceResult.objects.filter(stage=selected_stage, track=selected_track).order_by('position')

    return render(request, 'result/race_result_list.html', {
        'stages': stages,
        'selected_stage': selected_stage,
        'selected_track': selected_track,
        'results': results
    })


@staff_member_required
def edit_race_result(request, result_id):
    """
    Leidžia keisti varžybų rezultatus, bet tik staff
    :param request:
    :param result_id:
    :return:
    """
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
    """
    Rodo prisijungusio naudotojo asmeninius varžybų rezultatus
    :param request:
    :return:
    """
    user_profile = request.user.userprofile
    results = RaceResult.objects.filter(user_profile=user_profile).order_by('stage__date')
    total_points = results.aggregate(Sum('points'))['points__sum'] or 0
    return render(request, 'result/personal_results.html', {
        'results': results,
        'total_points': total_points,
    })


def team_results(request):
    """
    Rodo prisijungusio naudotojo komandos rezultatus
    :param request:
    :return:
    """
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
    """
    Rodo visų naudotojų bendrus rezultatus
    :param request:
    :return:
    """
    user_scores = OverallUserScore.objects.all().order_by('-total_points')
    return render(request, 'result/overall_user_scores.html', {
        'user_scores': user_scores,
    })


def overall_team_scores(request):
    """
    Rodo visų komandų bendrus rezultatus
    :param request:
    :return:
    """
    team_scores = OverallTeamScore.objects.all().order_by('-total_points')
    return render(request, 'result/overall_team_scores.html', {
        'team_scores': team_scores,
    })


def participants_statistics(request, stage_id):
    """
    Statistika pagal etapą, kiek dalyvių yra komandoje, kiek yra vyrų/moterų, ir pagal trasą
    :param request:
    :param stage_id:
    :return:
    """
    stage = get_object_or_404(Stage, id=stage_id)
    participants_by_stage = RaceRegistration.objects.filter(stage=stage).values('stage__name').annotate(
        total=Count('user_profile', distinct=True))
    participants_by_team = RaceRegistration.objects.filter(stage=stage).values('user_profile__team__name').annotate(
        total=Count('user_profile', distinct=True))
    participants_by_gender = RaceRegistration.objects.filter(stage=stage).values('user_profile__gender').annotate(
        total=Count('user_profile', distinct=True))
    participants_by_track = RaceRegistration.objects.filter(stage=stage).values('track__name').annotate(
        total=Count('user_profile', distinct=True))

    context = {
        'stage': stage,
        'by_stage': participants_by_stage,
        'by_team': participants_by_team,
        'by_gender': participants_by_gender,
        'by_track': participants_by_track,
    }

    return render(request, 'statistics/participants_statistics.html', context)


def participants_by_track_statistics(request, stage_id):
    """
    Statistika pagal trasą konkrečiam etapui
    :param request:
    :param stage_id:
    :return:
    """
    stage = get_object_or_404(Stage, id=stage_id)
    participants_by_track = RaceRegistration.objects.filter(stage=stage).values('track__name').annotate(
        total=Count('user_profile', distinct=True))

    context = {
        'stage': stage,
        'by_track': participants_by_track,
    }

    return render(request, 'statistics/participants_by_track_statistics.html', context)

def team_results_statistics(request):
    """
    Komandų rezultatų statistika
    :param request:
    :return:
    """
    stages = Stage.objects.all()
    team_list = []

    for stage in stages:
        stage_results = RaceResult.objects.filter(stage=stage).values('user_profile__team__name').annotate(
            total_points=Sum('points')).order_by('-total_points')
        team_list.append({
            'stage': stage,
            'results': stage_results
        })

    teams_paginator = Paginator(team_list, 10)  # 10 komandų viename puslapyje
    teams_page_number = request.GET.get('teams_page')
    teams_page_obj = teams_paginator.get_page(teams_page_number)

    return render(request, 'statistics/team_results_statistics.html', {
        'teams_page_obj': teams_page_obj,
        'stages': stages
    })


def filtered_results(request):
    stage_form = StageForm(request.GET or None)
    track_form = None
    results = RaceResult.objects.none()

    if stage_form.is_valid():
        stage = stage_form.cleaned_data.get('stage')
        track_form = TrackForm(stage, request.GET or None)

        if track_form.is_valid():
            track = track_form.cleaned_data.get('track')
            results = RaceResult.objects.filter(stage=stage, track=track)

    context = {
        'stage_form': stage_form,
        'track_form': track_form,
        'results': results
    }
    return render(request, 'result/filtered_results.html', context)


@login_required
def confirm_remove_registration(request, registration_id):
    registration = get_object_or_404(RaceRegistration, id=registration_id)
    return render(request, 'race_registration/confirm_remove_registration.html', {'registration': registration})


@login_required
def remove_registration(request, registration_id):
    registration = get_object_or_404(RaceRegistration, id=registration_id)
    if request.method == 'POST':
        registration.delete()
        return redirect('profile')
    return redirect('race_registration/confirm_remove_registration.html', registration_id=registration_id)


def stage_results(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)
    results = RaceResult.objects.filter(stage=stage).order_by('position')
    return render(request, 'result/stage_results.html', {'stage': stage, 'results': results})


def stage_participants(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)
    participants = RaceRegistration.objects.filter(stage=stage)
    for participant in participants:
        participant.full_name = f"{participant.user_profile.user.first_name} {participant.user_profile.user.last_name}"
    return render(request, 'race_registration/stage_participants.html', {'stage': stage, 'participants': participants})


def stage_participants_by_track(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)
    tracks = Track.objects.filter(stages=stage)
    track_participants = {track: RaceRegistration.objects.filter(stage=stage, track=track) for track in tracks}

    context = {
        'stage': stage,
        'track_participants': track_participants
    }
    return render(request, 'race_registration/participants_by_track.html', context)
