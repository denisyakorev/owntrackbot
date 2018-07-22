from django.urls import path
from bot import views
from django.contrib import admin

urlpatterns = [
    path('', views.dispatcher),
    path('admin/', admin.site.urls),
]
