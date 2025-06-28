from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import date

# Opciones para roles de usuario
ROL_CHOICES = [
    ('estudiante', 'Estudiante'),
    ('profesor', 'Profesor'),
]

# Opciones para el estado de misiones
ESTADO_MISION_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('completada', 'Completada'),
    ('en_progreso', 'En progreso'),
    ('fallida', 'Fallida'),
]

# Usuario personalizado
class CustomUser(AbstractUser):
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='estudiante')

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='Los grupos a los que pertenece este usuario.'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',
        blank=True,
        help_text='Permisos específicos para este usuario.'
    )

    def __str__(self):
        return self.username

# Personaje del usuario
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

# Clase escolar
class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    grado = models.CharField(max_length=50)
    profesor = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'profesor'})

    def __str__(self):
        return self.nombre

# Equipo dentro de una clase
class Equipo(models.Model):
    nombre_equipo = models.CharField(max_length=100)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_equipo

# Misión asignada a una clase
class Mision(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_entrega = models.DateField()
    puntos_xp = models.IntegerField()
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

# Relación entre personaje y equipo
class PersonajeEquipo(models.Model):
    personaje = models.ForeignKey(Personaje, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if PersonajeEquipo.objects.filter(equipo=self.equipo).count() >= 4:
            raise ValueError("Este equipo ya tiene el máximo de 4 integrantes.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.personaje} en {self.equipo}"

class PersonajeMision(models.Model):
    personaje = models.ForeignKey(Personaje, on_delete=models.CASCADE)
    mision = models.ForeignKey(Mision, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_MISION_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.personaje} - {self.mision} ({self.estado})"

    def verificar_entrega(self):
        if self.estado == 'pendiente' and self.mision.fecha_entrega < date.today():
            self.estado = 'vencida'
            self.personaje.vida = max(self.personaje.vida - 10, 0)  # castigo por no entregar
            self.personaje.save()
            self.save()
