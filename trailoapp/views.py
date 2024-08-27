from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Stage, Team, RaceRegistration, Track, RaceResult, OverallTeamScore, OverallUserScore
from .forms import UserUpdateForm, ProfileUpdateForm, TrackForm, StageForm, StageCreationForm



def home(request):
    """
    Rodo pradinį puslapį su būsimais ir praėjusiais etapais
    """
    now = timezone.now()  # Dabartinis laikas
    upcoming_stages = Stage.objects.filter(date__gte=now).order_by('date')  # Būsimi etapai
    past_stages = Stage.objects.filter(date__lt=now).order_by('-date')  # Praėję etapai
    context = {
        'upcoming_stages': upcoming_stages,
        'past_stages': past_stages,
        'now': now,
    }
    return render(request, 'home.html', context)


def all_stages(request):
    """
    Rodo visus etapus su dabartiniu laiku
    """
    stages = Stage.objects.all().order_by('-date')  # Visi etapai, pagal data
    now = timezone.now()  # Dabartinis laikas
    return render(request, 'all_stages.html', {'stages': stages, 'now': now})


def stage_detail(request, id):
    """
    Rodo detalią informacija apie pasirinkta etapą ir patvirtintas registracijas
    """
    stage = get_object_or_404(Stage, id=id)  # Suranda etapą pagal ID arba grąžina 404 klaidą
    registrations = RaceRegistration.objects.filter(stage=stage, status='p')  # Patvirtintos registracijos
    now = timezone.now()  # Dabartinis laikas
    context = {
        'stage': stage,
        'registrations': registrations,
        'now': now
    }
    return render(request, 'stage_detail.html', context)


@csrf_protect
def register_user(request):
    """
    Vartotojo registracija
    """
    if request.method == 'GET':
        teams = Team.objects.all()  # Visos komandos
        return render(request, 'registration/registration.html', {'teams': teams})  # Grąžina registracijos formą

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

        errors = []  # Klaidų sąrašas

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

        if errors:  # Jei yra klaidų, grąžinama atgal į registracijos formą su klaidų pranešimais.
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
    """
    Rodo prisijungusio vartotojo profilį
    """
    user_profile = request.user.userprofile  # Prisijungusio vartotojo profilis
    registrations = RaceRegistration.objects.filter(user_profile=user_profile)  # Vartotojo registracijos

    for registration in registrations:
        if timezone.now() > registration.stage.registration_end:
            registration.status = 'Registracija baigėsi'
        else:
            registration.status = 'Registracija galima'

    return render(request, 'profile.html', {'registrations': registrations})  # Grąžina profilio puslapį


@login_required
def edit_profile(request):
    """
    Leidžia vartotojui redaguoti savo profilį
    """
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

    return render(request, 'edit_profile.html', context)  # Grąžina profilio redagavimo puslapį


@staff_member_required
def review_registrations(request, stage_id):
    """
    Leidžia adminui peržiūrėti ir atnaujinti visų paraiškų statusą pagal etapą
    """
    stage = get_object_or_404(Stage, id=stage_id)  # Suranda etapą pagal ID arba grąžina 404 klaidą
    registrations = RaceRegistration.objects.filter(stage=stage)  # Visi registracijos į tą etapą

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

        return redirect("review_registrations", stage_id=stage.id)  # Nukreipia atgal į registracijų peržiūrą

    for registration in registrations:
        registration.full_name = f"{registration.user_profile.user.first_name} {registration.user_profile.user.last_name}"

    return render(request, 'race_registration/review_registrations.html',
                  {'stage': stage, 'registrations': registrations})  # Grąžina registracijų peržiūros puslapį


@login_required
def register_for_race(request):
    """
    Leidžia vartotojui užsiregistruoti į pasirinktą etapą
    """
    now = timezone.now()  # Dabartinis laikas
    stages = Stage.objects.filter(registration_end__gt=now)  # Etapai, kurių registracija dar nepasibaigusi

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
            return redirect('participants_list', stage_id=selected_stage.id)  # Nukreipia į dalyvių sąrašą
        else:
            registration = RaceRegistration(user_profile=user_profile, stage=selected_stage, track=track)
            registration.save()
            messages.success(request, 'Jūs sėkmingai užsiregistravote į etapą!')
            return redirect('participants_list', stage_id=selected_stage.id)  # Nukreipia į dalyvių sąrašą

    return render(request, 'race_registration/register_for_race.html', {
        'stages': stages,
        'tracks': tracks,
        'selected_stage_id': stage_id,
        'selected_stage': selected_stage,
        'now': now
    })  # Grąžina registracijos formą


def participants_list(request, stage_id):
    """
    Rodo sąrašą dalyvių, kurie užsiregistravę į konkretų etapą
    """
    stage = get_object_or_404(Stage, id=stage_id)  # Suranda etapą pagal ID arba grąžina 404 klaidą
    registrations = RaceRegistration.objects.filter(stage=stage)  # Dalyvių registracijos
    return render(request, 'race_registration/participants_list.html',
                  {'stage': stage, 'registrations': registrations})  # Grąžina dalyvių sąrašą


def race_result_list(request):
    """
    Rodo visus varžybų rezultatus pagal pasirinktą etapą ir trasą
    """
    stages = Stage.objects.all()  # Visi etapai
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
    })  # Grąžina rezultatų sąrašą


def personal_results(request):
    """
    Rodo prisijungusio naudotojo asmeninius varžybų rezultatus
    """
    user_profile = request.user.userprofile  # Prisijungusio vartotojo profilis
    results = RaceResult.objects.filter(user_profile=user_profile).order_by('stage__date')  # Vartotojo rezultatai
    total_points = results.aggregate(Sum('points'))['points__sum'] or 0  # Vartotojo taškų suma
    return render(request, 'result/personal_results.html', {
        'results': results,
        'total_points': total_points,
    })  # Grąžina asmeninių rezultatų puslapį


def team_results(request):
    """
    Rodo prisijungusio naudotojo komandos rezultatus
    """
    if not request.user.userprofile.team:
        messages.error(request, 'Jūs nepriklausote komandai.')
        return redirect('home')

    team = request.user.userprofile.team  # Vartotojo komanda
    results = RaceResult.objects.filter(user_profile__team=team).order_by('stage__date')  # Komandos rezultatai
    team_scores = results.values('stage__name').annotate(total_points=Sum('points')).order_by(
        'stage__date')  # Komandos taškai pagal etapą
    return render(request, 'result/team_results.html', {
        'team': team,
        'results': results,
        'team_scores': team_scores,
    })  # Grąžina komandos rezultatų puslapį


def overall_user_scores(request):
    """
    Rodo visų naudotojų bendrus rezultatus
    """
    user_scores = OverallUserScore.objects.all().order_by('-total_points')  # Visi naudotojų bendri rezultatai
    return render(request, 'result/overall_user_scores.html', {
        'user_scores': user_scores,
    })  # Grąžina bendrų naudotojų rezultatų puslapį


def overall_team_scores(request):
    """
    Rodo visų komandų bendrus rezultatus
    """
    team_scores = OverallTeamScore.objects.all().order_by('-total_points')  # Visi komandų bendri rezultatai
    return render(request, 'result/overall_team_scores.html', {
        'team_scores': team_scores,
    })  # Grąžina bendrų komandų rezultatų puslapį


def participants_statistics(request, stage_id):
    """
    Rodo dalyvių statistiką pagal etapą
    """
    stage = get_object_or_404(Stage, id=stage_id)  # Suranda etapą pagal ID arba grąžina 404 klaidą
    participants_by_stage = RaceRegistration.objects.filter(stage=stage).values('stage__name').annotate(
        total=Count('user_profile', distinct=True))  # Dalyvių skaičius pagal etapą
    participants_by_team = RaceRegistration.objects.filter(stage=stage).values('user_profile__team__name').annotate(
        total=Count('user_profile', distinct=True))  # Dalyvių skaičius pagal komandą
    participants_by_gender = RaceRegistration.objects.filter(stage=stage).values('user_profile__gender').annotate(
        total=Count('user_profile', distinct=True))  # Dalyvių skaičius pagal lytį
    participants_by_track = RaceRegistration.objects.filter(stage=stage).values('track__name').annotate(
        total=Count('user_profile', distinct=True))  # Dalyvių skaičius pagal trasą

    context = {
        'stage': stage,
        'by_stage': participants_by_stage,
        'by_team': participants_by_team,
        'by_gender': participants_by_gender,
        'by_track': participants_by_track,
    }

    return render(request, 'statistics/participants_statistics.html', context)  # Grąžina dalyvių statistikos puslapį


def participants_by_track_statistics(request, stage_id):
    """
    Rodo dalyvių statistiką pagal trasą konkrečiam etapui
    """
    stage = get_object_or_404(Stage, id=stage_id)  # Suranda etapą pagal ID arba grąžina 404 klaidą
    participants_by_track = RaceRegistration.objects.filter(stage=stage).values('track__name').annotate(
        total=Count('user_profile', distinct=True))  # Dalyvių skaičius pagal trasą

    context = {
        'stage': stage,
        'by_track': participants_by_track,
    }

    return render(request, 'statistics/participants_by_track_statistics.html',
                  context)  # Grąžina dalyvių pagal trasą statistikos puslapį


def team_results_statistics(request):
    """
    Rodo komandų rezultatų statistiką
    """
    stages = Stage.objects.all()  # Visi etapai
    team_list = []

    for stage in stages:
        stage_results = RaceResult.objects.filter(stage=stage).values('user_profile__team__name').annotate(
            total_points=Sum('points')).order_by('-total_points')  # Komandų rezultatai pagal etapą
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
    })  # Grąžina komandų rezultatų statistikos puslapį


def filtered_results(request):
    """
    Rodo filtruotus rezultatus pagal etapą ir trasą
    """
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
    return render(request, 'result/filtered_results.html', context)  # Grąžina filtruotų rezultatų puslapį


@login_required
def confirm_remove_registration(request, registration_id):
    """
    Patvirtina registracijos pašalinimą
    """
    registration = get_object_or_404(RaceRegistration,
                                     id=registration_id)  # Suranda registraciją pagal ID arba grąžina 404 klaidą
    return render(request, 'race_registration/confirm_remove_registration.html',
                  {'registration': registration})  # Grąžina registracijos pašalinimo patvirtinimo puslapį


@login_required
def remove_registration(request, registration_id):
    """
    Pašalina registraciją
    """
    registration = get_object_or_404(RaceRegistration,
                                     id=registration_id)  # Suranda registraciją pagal ID arba grąžina 404 klaidą
    if request.method == 'POST':
        registration.delete()
        return redirect('profile')  # Nukreipia į profilio puslapį
    return redirect('race_registration/confirm_remove_registration.html',
                    registration_id=registration_id)  # Nukreipia į registracijos pašalinimo patvirtinimo puslapį


def stage_results(request, stage_id):
    """
    Rodo etapo rezultatus
    """
    stage = get_object_or_404(Stage, id=stage_id)  # Suranda etapą pagal ID arba grąžina 404 klaidą
    results = RaceResult.objects.filter(stage=stage).order_by('position')  # Etapo rezultatai
    return render(request, 'result/stage_results.html',
                  {'stage': stage, 'results': results})  # Grąžina etapo rezultatų puslapį


def stage_participants(request, stage_id):
    """
    Rodo etapo dalyvius
    """
    stage = get_object_or_404(Stage, id=stage_id)  # Suranda etapą pagal ID arba grąžina 404 klaidą
    participants = RaceRegistration.objects.filter(stage=stage)  # Dalyviai pagal etapą
    for participant in participants:
        participant.full_name = f"{participant.user_profile.user.first_name} {participant.user_profile.user.last_name}"
    return render(request, 'race_registration/stage_participants.html',
                  {'stage': stage, 'participants': participants})  # Grąžina dalyvių pagal etapą puslapį


def stage_participants_by_track(request, stage_id):
    """
    Rodo dalyvių skaičių pagal trasą konkrečiam etapui
    """
    stage = get_object_or_404(Stage, id=stage_id)  # Suranda etapą pagal ID arba grąžina 404 klaidą
    tracks = Track.objects.filter(stages=stage)  # Trasos pagal etapą
    track_participants = {track: RaceRegistration.objects.filter(stage=stage, track=track) for track in
                          tracks}  # Dalyviai pagal trasas

    context = {
        'stage': stage,
        'track_participants': track_participants
    }
    return render(request, 'race_registration/participants_by_track.html',
                  context)


def search_stages(request):
    """
    Paieska pagal etapa
    :param request:
    :return:
    """
    query = request.GET.get('q')
    results = Stage.objects.filter(name__icontains=query) if query else []
    return render(request, 'search_results.html', {'query': query, 'results': results})


def create_stage(request):
    if request.method == 'POST':
        form = StageCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_stages')  # Nukreipimas į etapų sąrašą arba kitą tinkamą puslapį
    else:
        form = StageCreationForm()
    return render(request, 'create_stage.html', {'form': form})
