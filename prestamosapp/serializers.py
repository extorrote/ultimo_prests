
#ESTO ES PARA EL BUSCADOR EN TIEMPO REAL 
from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellidos']