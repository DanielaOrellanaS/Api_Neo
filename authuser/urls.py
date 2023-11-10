from django.urls import path, include
from authuser import views
from rest_framework import routers
from dj_rest_auth.views import LoginView

# routes endpoints
router = routers.DefaultRouter()
router.register(r'user', views.UserApiView, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('rest-auth/login/', LoginView.as_view(), name='rest_login')
    ]
    