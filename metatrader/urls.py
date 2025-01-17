from django.urls import path, include
from metatrader import views
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

# routes endpoints
router = routers.DefaultRouter()
router.register(r'moneda', views.MonedaApiView, basename='monedas')
router.register(r'par', views.ParesApiView, basename='pares')
router.register(r'tipocuenta', views.AccountTypeApiView, basename='tipocuenta')
router.register(r'cuenta', views.AccountApiView, basename='cuenta')
router.register(r'detallebalance', views.DetailBalanceAccountApiView, basename='detallebalance')
router.register(r'operaciones', views.OperationApiView, basename='operaciones')
router.register(r'neobot', views.robot_neoApiView, basename='neobot')
router.register(r'last_indicator', views.LastIndicatorApiView, basename='last_indicator')
router.register(r'cuentafavorita', views.UserFavAccountsApiView, basename='cuentasfavoritas')
router.register(r'eventos', views.EventsApiView, basename='eventos')
router.register(r'par_moneda', views.ParMonedaApiView, basename='par_moneda')
router.register(r'pips', views.PipsApiView, basename='pips')
router.register(r'rangos_indicador', views.rangos_neoApiView, basename='neobot')
router.register(r'resumetable', views.ResumeDetailBalanceApiView, basename='resumetable')
router.register(r'alldetailbalance', views.AllDetailBalanceApiView, basename='alldetailbalance')
router.register(r'alertaeventos', views.AlertEventsApiView, basename='alertaeventos')
router.register(r'token', views.DeviceTokenApiView, basename='token')
router.register(r'neobotpips', views.robot_neopipsApiView, basename='neobot')
router.register(r'sentnotification', views.SentNotificationAllDevices, basename='sentnotification')
router.register(r'notification', views.NotificationApiView, basename='notification')
router.register(r'tendencia', views.TendenciaApiView, basename='tendencia')
router.register(r'result_files', views.ResultFilesApiView, basename='result_files')

urlpatterns = [
    path('', include(router.urls)), 
    path('dispatcher/', views.dispatcher_view, name='dispatcher'),
    ]
