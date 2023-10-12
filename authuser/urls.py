from django.urls import path, include
from authuser import views
from rest_framework import routers

# routes endpoints
router = routers.DefaultRouter()
router.register(r'user', views.UserApiView, basename='user')

urlpatterns = [
    path('', include(router.urls)), 
    ]
    