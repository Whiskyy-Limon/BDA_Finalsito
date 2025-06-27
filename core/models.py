from django.db import models
from django.contrib.auth.models import AbstractUser

ROL_CHOICES = [
    ('estudiante', 'Estudiante'),
    ('profesor', 'Profesor'),
]

ESTADO_MISION_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('completada', 'Completada'),
    ('en_progreso', 'En progreso'),
]

class CustomUser(AbstractUser):
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='estudiante')

    def __str__(self):
        return self.username

class Personaje(models.Model):
    RAZAS = [
        ('Elfo', 'Elfo'),
        ('Enano', 'Enano'),
        ('Mago', 'Mago'),
        ('Humano', 'Humano'),
        ('Orco', 'Orco'),
    ]

    usuario = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    raza = models.CharField(max_length=20, choices=RAZAS)
    experiencia = models.IntegerField(default=0)
    nivel = models.IntegerField(default=1)
    vida = models.IntegerField(default=100)
    mana = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.usuario.username} - {self.raza}"

    def ganar_experiencia(self, cantidad):
        self.experiencia += cantidad
        while self.experiencia >= self.nivel * 100:
            self.experiencia -= self.nivel * 100
            self.nivel += 1
        self.save()

# Clase
class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    grado = models.CharField(max_length=50)
    profesor = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'profesor'})

    def __str__(self):
        return self.nombre

# Equipo
class Equipo(models.Model):
    nombre_equipo = models.CharField(max_length=100)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_equipo

# Misión
class Mision(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_entrega = models.DateField()
    puntos_xp = models.IntegerField()
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

# Relación Personaje-Equipo
class PersonajeEquipo(models.Model):
    personaje = models.ForeignKey(Personaje, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.personaje} en {self.equipo}"

# Relación Personaje-Misión
class PersonajeMision(models.Model):
    personaje = models.ForeignKey(Personaje, on_delete=models.CASCADE)
    mision = models.ForeignKey(Mision, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_MISION_CHOICES, default='pendiente')
