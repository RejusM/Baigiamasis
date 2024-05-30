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
]
