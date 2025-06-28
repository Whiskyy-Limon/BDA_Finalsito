from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Clase, Personaje, Mision, PersonajeMision, Equipo, PersonajeEquipo
from .forms import RegistroForm, ClaseForm, EquipoForm, MisionForm
from django.utils import timezone
from django.db.models import Q
from datetime import date

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

@login_required
def detalle_clase(request, clase_id):
    clase = Clase.objects.get(id=clase_id)

    # ✅ Solución aquí:
    personajes = Personaje.objects.filter(personajeequipo__equipo__clase=clase).distinct()

    for p in personajes:
        xp_total = p.nivel * 100
        p.porcentaje_xp = round((p.experiencia / xp_total) * 100) if xp_total > 0 else 0

    misiones = Mision.objects.filter(clase=clase)
    equipos = Equipo.objects.filter(clase=clase)
    form_equipo = EquipoForm(user=request.user, initial={'clase': clase})

    if request.method == 'POST':
        if 'crear_equipo' in request.POST:
            form_equipo = EquipoForm(request.POST, user=request.user)
            if form_equipo.is_valid():
                nuevo_equipo = form_equipo.save(commit=False)
                nuevo_equipo.clase = clase
                nuevo_equipo.save()
                messages.success(request, 'Equipo creado con éxito.')
                return redirect('detalle_clase', clase_id=clase_id)

        elif 'asignar_estudiante' in request.POST:
            personaje_id = request.POST.get('personaje_id')
            equipo_id = request.POST.get('equipo_id')

            personaje = get_object_or_404(Personaje, id=personaje_id)
            equipo = get_object_or_404(Equipo, id=equipo_id)

            if PersonajeEquipo.objects.filter(equipo=equipo).count() >= 4:
                messages.error(request, 'Este equipo ya tiene 4 integrantes.')
            elif PersonajeEquipo.objects.filter(personaje=personaje).exists():
                messages.warning(request, f'{personaje.usuario.username} ya pertenece a un equipo.')
            else:
                PersonajeEquipo.objects.create(personaje=personaje, equipo=equipo)
                messages.success(request, f'{personaje.usuario.username} fue asignado a {equipo.nombre_equipo}.')

            return redirect('detalle_clase', clase_id=clase_id)

    return render(request, 'core/detalle_clase.html', {
        'clase': clase,
        'personajes': personajes,
        'misiones': misiones,
        'equipos': equipos,
        'form_equipo': form_equipo
    })          

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

@login_required
def crear_clase(request):
    if request.user.rol != 'profesor':
        return redirect('login')  # o puedes mostrar un error

    if request.method == 'POST':
        form = ClaseForm(request.POST)
        if form.is_valid():
            clase = form.save(commit=False)
            clase.profesor = request.user
            clase.save()
            return redirect('crear_clase')  # o redirigir a otra vista
    else:
        form = ClaseForm()
    
    return render(request, 'profesor/crear_clase.html', {'form': form})

@login_required
def crear_equipo(request):
    if request.user.rol != 'profesor':
        return redirect('login')

    if request.method == 'POST':
        form = EquipoForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('crear_equipo')
    else:
        form = EquipoForm(user=request.user)

    return render(request, 'profesor/crear_equipo.html', {'form': form})

@login_required
def crear_mision(request):
    if request.user.rol != 'profesor':
        return redirect('login')

    if request.method == 'POST':
        form = MisionForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('crear_mision')
    else:
        form = MisionForm(user=request.user)

    return render(request, 'profesor/crear_mision.html', {'form': form})

@login_required
def unirse_a_equipo(request, equipo_id):
    if request.user.rol != 'estudiante':
        return redirect('login')

    equipo = get_object_or_404(Equipo, id=equipo_id)
    personaje = get_object_or_404(Personaje, usuario=request.user)

    miembros_equipo = PersonajeEquipo.objects.filter(equipo=equipo)

    if miembros_equipo.filter(personaje=personaje).exists():
        messages.warning(request, 'Ya perteneces a este equipo.')
    elif miembros_equipo.count() >= 4:
        messages.error(request, 'Este equipo ya tiene el máximo de 4 miembros.')
    else:
        PersonajeEquipo.objects.create(personaje=personaje, equipo=equipo)
        messages.success(request, f'Te has unido al equipo {equipo.nombre_equipo}.')

    return redirect('listar_equipos')

@login_required
def listar_equipos(request):
    if request.user.rol != 'estudiante':
        return redirect('login')

    equipos = Equipo.objects.all()
    return render(request, 'alumno/listar_equipos.html', {'equipos': equipos})

@login_required
def descontar_vida_misiones_vencidas(request):
    if request.user.rol != 'profesor':
        return redirect('login')

    clases_profesor = Clase.objects.filter(profesor=request.user)
    misiones = Mision.objects.filter(clase__in=clases_profesor, fecha_entrega__lt=timezone.now())

    contador = 0

    for mision in misiones:
        relaciones = PersonajeMision.objects.filter(
            mision=mision,
            estado__in=['pendiente', 'en_progreso']
        )

        for relacion in relaciones:
            personaje = relacion.personaje
            if personaje.vida > 0:
                personaje.vida = max(0, personaje.vida - 20)
                personaje.save()
                contador += 1

    messages.success(request, f'Se descontó vida a {contador} personajes con misiones no entregadas.')
    return redirect('panel_profesor')

@login_required
def estado_entregas(request):
    if request.user.rol != 'profesor':
        return redirect('login')

    clases = Clase.objects.filter(profesor=request.user)
    misiones = Mision.objects.filter(clase__in=clases).order_by('-fecha_entrega')
    entregas = PersonajeMision.objects.filter(mision__in=misiones).select_related('personaje__usuario', 'mision')

    contexto = {
        'entregas': entregas
    }
    return render(request, 'profesor/estado_entregas.html', contexto)

@login_required
def unirse_grupo(request, clase_id):
    if request.user.rol != 'estudiante':
        return redirect('panel_profesor')

    clase = get_object_or_404(Clase, id=clase_id)
    personaje = get_object_or_404(Personaje, usuario=request.user)

    if request.method == 'POST':
        grupo_id = request.POST.get('grupo_id')
        equipo = get_object_or_404(Equipo, id=grupo_id)

        cantidad_integrantes = PersonajeEquipo.objects.filter(equipo=equipo).count()
        ya_esta = PersonajeEquipo.objects.filter(personaje=personaje).exists()

        if cantidad_integrantes >= 4:
            return render(request, 'alumno/unirse_grupo.html', {
                'clase': clase,
                'grupos': clase.equipo_set.all(),
                'error': 'Este grupo ya tiene el máximo de integrantes.'
            })

        if ya_esta:
            return render(request, 'alumno/unirse_grupo.html', {
                'clase': clase,
                'grupos': clase.equipo_set.all(),
                'error': 'Ya perteneces a un grupo.'
            })

        PersonajeEquipo.objects.create(personaje=personaje, equipo=equipo)
        return redirect('panel_alumno')  # o donde quieras redirigir

    grupos = clase.equipo_set.all()
    return render(request, 'alumno/unirse_grupo.html', {'clase': clase, 'grupos': grupos})

@login_required
def descontar_vida(request, clase_id):
    if request.user.rol != 'profesor':
        return redirect('panel_alumno')

    clase = get_object_or_404(Clase, id=clase_id)
    misiones_vencidas = Mision.objects.filter(clase=clase, fecha_entrega__lt=date.today())
    
    afectados = []

    for mision in misiones_vencidas:
        pendientes = PersonajeMision.objects.filter(mision=mision, estado='pendiente')
        for pm in pendientes:
            personaje = pm.personaje
            personaje.vida = max(personaje.vida - 10, 0)
            personaje.save()
            pm.estado = 'fallida'
            pm.save()
            afectados.append(personaje.usuario.username)

    messages.success(request, f"Se descontó vida a: {', '.join(set(afectados))}" if afectados else "No hubo alumnos con misiones pendientes.")
    return redirect('panel_profesor')

@login_required
def quitar_estudiante_equipo(request):
    if request.method == 'POST' and request.user.rol == 'profesor':
        relacion_id = request.POST.get('relacion_id')
        clase_id = request.POST.get('clase_id')

        relacion = get_object_or_404(PersonajeEquipo, id=relacion_id)
        relacion.delete()
        messages.success(request, f"{relacion.personaje.usuario.username} fue removido del equipo.")

        return redirect('detalle_clase', clase_id=clase_id)
    return redirect('panel_profesor')
