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
router.register(r'detallebalancedia', views.DetailBalanceDayApiView, basename='detallebalancedia')
router.register(r'operaciones', views.OperationApiView, basename='operaciones')
router.register(r'numoperaciones', views.OperationCountApiView, basename='numoperaciones')
router.register(r'operacionesabiertas', views.OpenOperationApiView, basename='operacionesabiertas')
router.register(r'operacionescerradas', views.CloseOperationApiView, basename='operacionescerradas')
router.register(r'neobot', views.robot_neoApiView, basename='neobot')
router.register(r'last_indicator', views.LastIndicatorApiView, basename='last_indicator')
router.register(r'cuentafavorita', views.UserFavAccountsApiView, basename='cuentasfavoritas')

urlpatterns = [
    path('', include(router.urls)), 
    ]
    