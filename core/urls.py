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
    path('profesor/dashboard/', views.profesor_dashboard, name='profesor_dashboard'),


]
