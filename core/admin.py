from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Maquinaria, Molde, RegistroConsumo, PrecioEnergia


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'rol', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('rol',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Maquinaria)
admin.site.register(Molde)
admin.site.register(RegistroConsumo)
admin.site.register(PrecioEnergia)

