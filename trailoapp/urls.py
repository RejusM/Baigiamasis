from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('stages/', views.all_stages, name='all_stages'),  # Visų etapų sąrašas
    path('stages/<int:id>/', views.stage_detail, name='stage_detail'),  # Etapo detalės
    path('register/', views.register_user, name='register'),  # Registracija svetainėje
    path('profile/', views.profile, name='profile'),  # Profilis
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # Profilio redagavimas
    path('race-register/', views.register_for_race, name='register_for_race'),  # Registracija į etapus
    path('results/', views.race_result_list, name='race_result_list'),  # Visų etapų rezultatų sąrašas
    path('results/add/', views.add_race_result, name='add_race_result'),  # Pridėti rezultatus
    path('results/edit/<int:result_id>/', views.edit_race_result, name='edit_race_result'),  # Rezultato redagavimas
    path('results/personal/', views.personal_results, name='personal_results'),  # Asmeniniai rezultatai
    path('results/team/', views.team_results, name='team_results'),  # Komandų rezultatai
    path('scores/users/', views.overall_user_scores, name='overall_user_scores'),  # Bendri dalyvių rezultatai
    path('scores/teams/', views.overall_team_scores, name='overall_team_scores'),  # Bendri komandų rezultatai
    path('participants-statistics/<int:stage_id>/', views.participants_statistics, name='participants_statistics'),  # Dalyvių statistika
    path('results-statistics/', views.results_statistics, name='results_statistics'),  # Rezultatų statistika
    path('team-results-statistics/', views.team_results_statistics, name='team_results_statistics'),  # Komandų rezultatų statistika
    path('filtered-results/', views.filtered_results, name='filtered_results'),  # Filtruoti rezultatai pagal trasą
    path('confirm-remove-registration/<int:registration_id>/', views.confirm_remove_registration, name='confirm_remove_registration'),  # pašalinti savo registracija
    path('remove-registration/<int:registration_id>/', views.remove_registration, name='remove_registration'),  # pašalintos registracijos patvirtinimas
    path('stages/<int:stage_id>/results/', views.stage_results, name='stage_results'),  # Etapo rezultatai
    path('stages/<int:stage_id>/participants/', views.stage_participants, name='stage_participants'),  # Etapo dalyviai
    path('stages/<int:stage_id>/review-registrations/', views.review_registrations, name='review_registrations'),  # Peržiūrėti paraiškas
    path('participants_by_track/<int:stage_id>/', views.stage_participants_by_track, name='participants_by_track'),  # Dalyvių sąrašas pagal trasas
]
