from django.urls import path
from .views import ListaUsuariosView, EditarUsuarioView, PerfilUsuarioView, CustomPasswordChangeView, CambiarRolUsuarioForm, CambiarRolUsuarioView, CrearUsuarioView

urlpatterns = [
    path("editar/<int:pk>/", EditarUsuarioView.as_view(), name="editar-usuario"),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil-usuario'),
    path("cambiar-contrasena/", CustomPasswordChangeView.as_view(), name="cambiar-contrasena"),
    path('lista/', ListaUsuariosView.as_view(), name='lista-usuarios'),
    path('cambiar-rol/<int:pk>/', CambiarRolUsuarioView.as_view(), name='cambiar-rol'),
    path('crear/', CrearUsuarioView.as_view(), name='crear-usuario'),
]
