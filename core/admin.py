from django.contrib import admin
from .models import CustomUser, Clase, Personaje, Equipo, Mision, PersonajeEquipo, PersonajeMision

admin.site.register(CustomUser)
admin.site.register(Personaje)
admin.site.register(Clase)
admin.site.register(Equipo)
admin.site.register(Mision)
admin.site.register(PersonajeEquipo)
admin.site.register(PersonajeMision)
