from django.urls import path
from bot import views

urlpatterns = [
    path('hello_world/', views.hello_world),
    path('565321270:AAGVaNTz5a2pscli1_VnG0vh2Fv0CarejLM/', views.dispatcher),
]