from django.urls import path, include
from metatrader import views
from rest_framework import routers
from metatrader.views import SentNotifications, SentCustomNotifications

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
router.register(r'testpares', views.ParesApiViewCopy, basename='testpares')
router.register(r'testmonedas', views.MonedaApiViewCopy, basename='testmonedas')

urlpatterns = [
    path('', include(router.urls)), 
    path('notification/', SentNotifications.as_view(), name='notification'),
    path('customnotification/', SentCustomNotifications.as_view(), name='customnotification'),
    ]
    