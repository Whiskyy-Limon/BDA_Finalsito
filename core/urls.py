from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profesor/clase/<int:clase_id>/', views.detalle_clase, name='detalle_clase'),
    path('profesor/dashboard/', views.profesor_dashboard, name='panel_profesor'),
    path('profesor/clase/<int:clase_id>/crear_mision/', views.crear_mision, name='crear_mision'),
    path('estudiante/', views.panel_estudiante, name='panel_estudiante'),
    path('estudiante/mision/<int:pk>/completar/', views.completar_mision, name='completar_mision'),
    path('seleccion-personaje/', views.seleccion_personaje, name='seleccion_personaje'),
    path('asignar-personaje/<str:raza>/', views.asignar_personaje, name='asignar_personaje'),
    path('profesor/crear-clase/', views.crear_clase, name='crear_clase'),
    path('profesor/crear-equipo/', views.crear_equipo, name='crear_equipo'),
    path('profesor/crear-mision/', views.crear_mision, name='crear_mision'),
    path('alumno/unirse-grupo/<int:equipo_id>/', views.unirse_a_equipo, name='unirse_equipo'),
    path('alumno/equipos/', views.listar_equipos, name='listar_equipos'),
    path('profesor/descontar-vida/', views.descontar_vida_misiones_vencidas, name='descontar_vida'),
    path('profesor/estado-entregas/', views.estado_entregas, name='estado_entregas'),
    path('alumno/unirse-grupo/<int:clase_id>/', views.unirse_grupo, name='unirse_grupo'),
    path('profesor/descontar-vida/<int:clase_id>/', views.descontar_vida, name='descontar_vida'),
    path('profesor/equipo/quitar/', views.quitar_estudiante_equipo, name='quitar_estudiante_equipo'),
]
