from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Clase, Equipo, Mision

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        
class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clase
        fields = ['nombre', 'grado']

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre_equipo']  

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['clase'].queryset = Clase.objects.filter(profesor=user)
    
class MisionForm(forms.ModelForm):
    class Meta:
        model = Mision
        fields = ['titulo', 'descripcion', 'fecha_entrega', 'puntos_xp', 'clase']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['clase'].queryset = Clase.objects.filter(profesor=user)