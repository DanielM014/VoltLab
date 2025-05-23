from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import UpdateView, CreateView
from django.urls import reverse_lazy
from .forms import EditarUsuarioForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from .forms import CambiarRolUsuarioForm
from .forms import CrearUsuarioForm
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
User = get_user_model()


class ListaUsuariosView(UserPassesTestMixin, ListView):
    model = User
    template_name = 'usuarios/lista_usuarios.html'
    context_object_name = 'usuarios'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class EditarUsuarioView(UserPassesTestMixin, UpdateView):
    model = User
    form_class = EditarUsuarioForm
    template_name = 'usuarios/editar_usuario.html'
    success_url = reverse_lazy('listar-usuarios')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def form_valid(self, form):
        response = super().form_valid(form)

        grupo = form.cleaned_data.get('grupo')
        if grupo:
            self.object.groups.set([grupo])  # Solo uno a la vez
        else:
            self.object.groups.clear()

        return response
    
    from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class PerfilUsuarioView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        grupos = user.groups.all()
        context['usuario'] = user
        context['roles'] = grupos
        return context


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "usuarios/password_change_form.html"
    success_url = reverse_lazy("perfil-usuario")


    
class ListaUsuariosView(UserPassesTestMixin, ListView):
    model = User
    template_name = 'usuarios/lista_usuarios.html'
    context_object_name = 'usuarios'

    def test_func(self):
        return self.request.user.is_staff

class CambiarRolUsuarioView(UserPassesTestMixin, UpdateView):
    model = User
    form_class = CambiarRolUsuarioForm
    template_name = 'usuarios/cambiar_rol.html'
    success_url = reverse_lazy('lista-usuarios')

    def test_func(self):
        return self.request.user.is_staff
    
class CrearUsuarioView(CreateView):
    template_name = 'usuarios/crear_usuario.html'
    form_class = CrearUsuarioForm
    success_url = reverse_lazy('lista-usuarios')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        # Crear nuevo rol si se ingresó
        nuevo_rol = form.cleaned_data.get('nuevo_rol')
        if nuevo_rol:
            grupo, created = Group.objects.get_or_create(name=nuevo_rol)
        else:
            grupo = form.cleaned_data['grupo_existente']

        if grupo:
            user.groups.add(grupo)

        return super().form_valid(form)