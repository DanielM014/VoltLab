from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    MaquinariaListView,
    MaquinariaCreateView,
    MaquinariaUpdateView,
    MaquinariaDeleteView,
    MoldeListView,
    MoldeCreateView,
    MoldeUpdateView,
    MoldeDeleteView,
    RegistroConsumoCreateView,
    RegistroConsumoDeleteView,
    RegistroConsumoListView,
    dashboard_view,
    AsignacionCreateView,
    AsignacionDeleteView,
    AsignacionListView,
    AsignacionUpdateView,
    PrecioEnergiaView,
    PrecioEnergiaListView,
    SimuladorROIView,
    CambiarMesActivoView,
    MesActivoUpdateView
)


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('maquinaria/', MaquinariaListView.as_view(), name='maquinaria-list'),
    path('maquinaria/crear/', MaquinariaCreateView.as_view(), name='maquinaria-crear'),
    path('maquinaria/editar/<int:pk>/', MaquinariaUpdateView.as_view(), name='maquinaria-editar'),
    path('maquinaria/eliminar/<int:pk>/', MaquinariaDeleteView.as_view(), name='maquinaria-eliminar'),
    path('moldes/', MoldeListView.as_view(), name='molde-list'),
    path('moldes/crear/', MoldeCreateView.as_view(), name='molde-crear'),
    path('moldes/editar/<int:pk>/', MoldeUpdateView.as_view(), name='molde-editar'),
    path('moldes/eliminar/<int:pk>/', MoldeDeleteView.as_view(), name='molde-eliminar'),
    path('consumo/', RegistroConsumoListView.as_view(), name='consumo-list'),
    path('consumo/crear/', RegistroConsumoCreateView.as_view(), name='consumo-crear'),
    path('consumo/eliminar/<int:pk>/', RegistroConsumoDeleteView.as_view(), name='consumo-eliminar'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('asignaciones/', AsignacionListView.as_view(), name='asignacion-list'),
    path('asignaciones/crear/', AsignacionCreateView.as_view(), name='asignacion-crear'),
    path('asignaciones/editar/<int:pk>/', AsignacionUpdateView.as_view(), name='asignacion-editar'),
    path('asignaciones/eliminar/<int:pk>/', AsignacionDeleteView.as_view(), name='asignacion-eliminar'),
    path('precio-energia/', PrecioEnergiaView.as_view(), name='precio-energia'),
    path('historial-precios/', PrecioEnergiaListView.as_view(), name='precio-historial'),
    path('simulador-roi/', SimuladorROIView.as_view(), name='simulador-roi'),
    path('mes-activo/<int:pk>/editar/', CambiarMesActivoView.as_view(), name='cambiar-mes-activo'),
    path('mes-activo/', MesActivoUpdateView.as_view(), name='mes-activo'),
    path('ajax/maquinas/', views.obtener_maquinas_por_molde, name='ajax-obtener-maquinas'),

]