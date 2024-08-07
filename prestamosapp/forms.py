from django import forms
from .models import Cliente,Payment
from .models import AgregarGasto,AgregarBase

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['order','nombre', 'apellidos', 'monto', 'direccion', 'descripcion_casa', 'foto_casa']
        #ESTO LO AGREGUE PARA EL METODO DE EDITAR CLIENTE Y QUE ESTOS CAMPOS NO SE PUEDAN EDITAR, QUE SE MUESTREN PERO SOLO COMO readonlyfields
        widgets = {
            #'monto': forms.TextInput(attrs={'readonly': 'readonly'}), ESTO LO BORRE PORQUE NO ME DEJABA AGREGAR MONTO A LA HORA DE INGRESAR EL CLIENTE, LO QUE NO QUIERO ES QUE FUNCIONE A LA HORA DE EDITARLO.
            'monto_mas_interes': forms.TextInput(attrs={'readonly': 'readonly'}),
            'saldo': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        monto = cleaned_data.get('monto')
        if monto:
            cleaned_data['monto_mas_interes'] = monto * 1.20  # Example calculation for 20% interest
            cleaned_data['couta_diaria'] = cleaned_data['monto_mas_interes'] / 20  # Example calculation for 20 days
        return cleaned_data
        
        
        
        
 #AL PRINCIPIO HABIAMOS HECHO EL METODO DE PAGOS SIN UN MODELO PERO ASI NO LO ESTABA GUARDANDO EN EL database ASI QUE NO PODIA MOSTRAR EL HISTORIAL DE PAGOS ,     
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_amount']
        
        
        


class AgregarGastoForm(forms.ModelForm):
    class Meta:
        model = AgregarGasto
        fields = ['descripcion_gasto', 'monto_gasto']
        
        

class AgregarBaseForm(forms.ModelForm):
    class Meta:
        model = AgregarBase
        fields = ['descripcion_base', 'monto_base']