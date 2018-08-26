from django.urls import path
from core import views


urlpatterns = [
   path('profile_info/<str:profile_id>/', views.get_profile_info, name='profile info'),
]