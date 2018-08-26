from django.urls import path
from bot import views
from core import views as core_views
from django.contrib import admin

urlpatterns = [
    path('', views.dispatcher),
    path('profile_info/<str:profile_id>/', core_views.get_profile_info, name='profile info'),
]
