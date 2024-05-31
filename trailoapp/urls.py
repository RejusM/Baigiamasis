from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stages/', views.all_stages, name='all_stages'),
    path('stages/<int:id>/', views.stage_detail, name='stage_detail'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('registrations/', views.registration_list, name='registration_list'),
    path('registrations/<int:registration_id>/', views.review_registration, name='review_registration'),
    path('race-register/', views.register_for_race, name='register_for_race'),
    path('participants/<int:stage_id>/', views.participants_list, name='participants_list'),
    path('results/', views.race_result_list, name='race_result_list'),
    path('results/add/', views.add_race_result, name='add_race_result'),
    path('results/edit/<int:result_id>/', views.edit_race_result, name='edit_race_result'),
    path('results/personal/', views.personal_results, name='personal_results'),
    path('results/team/', views.team_results, name='team_results'),
    path('scores/users/', views.overall_user_scores, name='overall_user_scores'),
    path('scores/teams/', views.overall_team_scores, name='overall_team_scores'),

]
