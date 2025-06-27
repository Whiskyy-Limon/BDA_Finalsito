from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Clase, Personaje, Mision, PersonajeMision
from .forms import RegistroForm

def register_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registro exitoso. Bienvenido {user.username}")
            return redirect('seleccion_personaje')
        else:
            # Aquí mostramos todos los errores del formulario:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistroForm()
    return render(request, 'core/login.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.rol == 'profesor':
                return redirect('profesor_dashboard')
            else:
                return redirect('seleccion_personaje')
        else:
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'core/login.html', {'form': RegistroForm()})

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard Profesor
@login_required
def profesor_dashboard(request):
    clases = Clase.objects.filter(profesor=request.user)
    return render(request, 'core/profesor_dashboard.html', {'clases': clases})

# Detalle de clase
@login_required
def detalle_clase(request, clase_id):
    clase = Clase.objects.get(id=clase_id)
    personajes = Personaje.objects.filter(clase=clase)
    misiones = Mision.objects.filter(clase=clase)
    return render(request, 'core/detalle_clase.html', {
        'clase': clase,
        'personajes': personajes,
        'misiones': misiones
    })

# Crear misión
@login_required
def crear_mision(request, clase_id):
    if request.user.rol != 'profesor':
        return redirect('panel_estudiante')

    clase = Clase.objects.get(id=clase_id)
    if request.method == 'POST':
        mision = Mision.objects.create(
            titulo=request.POST['titulo'],
            descripcion=request.POST['descripcion'],
            fecha_entrega=request.POST['fecha_entrega'],
            puntos_xp=request.POST['puntos_xp'],
            clase=clase
        )

        personajes = Personaje.objects.filter(clase=clase)
        for personaje in personajes:
            PersonajeMision.objects.create(personaje=personaje, mision=mision)

        messages.success(request, "¡Misión creada y asignada a todos los estudiantes!")
        return redirect('detalle_clase', clase_id=clase_id)

    return redirect('detalle_clase', clase_id=clase_id)

# Dashboard Estudiante
@login_required
def panel_estudiante(request):
    try:
        personaje = Personaje.objects.get(usuario=request.user)
    except Personaje.DoesNotExist:
        return redirect('seleccion_personaje')

    misiones_personaje = PersonajeMision.objects.filter(personaje=personaje)
    return render(request, 'core/panel_estudiante.html', {
        'personaje': personaje,
        'misiones': misiones_personaje
    })

# Completar misión
@login_required
def completar_mision(request, pk):
    mision = PersonajeMision.objects.get(pk=pk)
    if mision.estado != 'completada':
        mision.estado = 'completada'
        mision.save()
        personaje = mision.personaje
        personaje.ganar_experiencia(mision.mision.puntos_xp)
        messages.success(request, f'¡Has completado la misión "{mision.mision.titulo}" y ganado {mision.mision.puntos_xp} XP!')
    return redirect('panel_estudiante')

# Selección de personaje
@login_required
def seleccion_personaje(request):
    return render(request, 'core/seleccion_personaje.html')

# Asignación de personaje
@login_required
def asignar_personaje(request, raza):
    atributos = {
        'Elfo': {'vida': 80, 'mana': 120},
        'Enano': {'vida': 150, 'mana': 60},
        'Mago': {'vida': 70, 'mana': 150},
        'Humano': {'vida': 100, 'mana': 100},
        'Orco': {'vida': 200, 'mana': 30},
    }

    if raza not in atributos:
        return redirect('seleccion_personaje')

    if Personaje.objects.filter(usuario=request.user).exists():
        return redirect('panel_estudiante')

    Personaje.objects.create(
        usuario=request.user,
        raza=raza,
        vida=atributos[raza]['vida'],
        mana=atributos[raza]['mana'],
        experiencia=0
    )

    return redirect('panel_estudiante')
