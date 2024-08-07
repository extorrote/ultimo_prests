from rest_framework import serializers
from paquete5.models import Cliente

#ESTO ES PARA EL BUSCADOR TAMBIEN
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellidos']