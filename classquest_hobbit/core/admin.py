from django.contrib import admin
from .models import Usuario, Raza, Clase, Personaje, Equipo, Mision, PersonajeEquipo, PersonajeMision

admin.site.register(Usuario)
admin.site.register(Raza)
admin.site.register(Clase)
admin.site.register(Personaje)
admin.site.register(Equipo)
admin.site.register(Mision)
admin.site.register(PersonajeEquipo)
admin.site.register(PersonajeMision)
