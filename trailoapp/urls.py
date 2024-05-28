from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stages/', views.all_stages, name='all_stages'),
    path('stages/<int:id>/', views.stage_detail, name='stage_detail'),

]