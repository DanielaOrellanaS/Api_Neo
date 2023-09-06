from django.urls import path, include
from metatrader import views
from rest_framework import routers

# routes endpoints
router = routers.DefaultRouter()
router.register(r'moneda', views.MonedaApiView, basename='monedas')
router.register(r'par', views.ParesApiView, basename='pares')
router.register(r'tipocuenta', views.AccountTypeApiView, basename='tipocuenta')
router.register(r'cuenta', views.AccountApiView, basename='cuenta')
router.register(r'detallebalance', views.DetailBalanceAccountApiView, basename='detallebalance')
router.register(r'operaciones', views.OperationApiView, basename='operaciones')

urlpatterns = [
    path('', include(router.urls)), 
    ]
    