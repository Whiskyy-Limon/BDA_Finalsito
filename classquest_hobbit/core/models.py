from django.db import models

# ENUMS simulados con choices
ROL_CHOICES = [
    ('estudiante', 'Estudiante'),
    ('profesor', 'Profesor'),
    ('admin', 'Administrador'),
]

ESTADO_MISION_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('completada', 'Completada'),
    ('en_progreso', 'En progreso'),
]

# MODELOS

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    contraseña = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)

    def __str__(self):
        return self.nombre

class Raza(models.Model):
    nombre_raza = models.CharField(max_length=50)
    descripcion = models.TextField()
    habilidad_especial = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_raza

class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    grado = models.CharField(max_length=50)
    profesor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'profesor'})

    def __str__(self):
        return self.nombre

class Personaje(models.Model):
    nombre_personaje = models.CharField(max_length=100)
    nivel = models.IntegerField(default=1)
    experiencia = models.IntegerField(default=0)
    vida = models.IntegerField(default=100)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'estudiante'})
    raza = models.ForeignKey(Raza, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre_personaje

class Equipo(models.Model):
    nombre_equipo = models.CharField(max_length=100)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_equipo

class Mision(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_entrega = models.DateField()
    puntos_xp = models.IntegerField()
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class PersonajeEquipo(models.Model):
    personaje = models.ForeignKey(Personaje, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.personaje} en {self.equipo}"

class PersonajeMision(models.Model):
    personaje = models.ForeignKey(Personaje, on_delete=models.CASCADE)
    mision = models.ForeignKey(Mision, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_MISION_CHOICES, default='pendiente')
