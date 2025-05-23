
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  
    path('roi/', include('roi.urls')),
    path("modelo/", include("regresion.urls")),
    path("reportes/", include("reportes.urls")),
    path("usuarios/", include("usuarios.urls")),
]
