from django.db import models
from django.utils import timezone
from datetime import timedelta



class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    monto = models.IntegerField()  # Amount of the loan
    monto_mas_interes = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Loan amount + 20% interest
    couta_diaria = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Daily installment
    saldo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Remaining balance
    direccion = models.CharField(max_length=100)
    descripcion_casa = models.TextField(default='null', verbose_name="Descripción de la Casa")
    foto_casa = models.ImageField(default='null', verbose_name="Foto de la Casa", upload_to='articulos')
    fecha_de_creacion = models.DateTimeField(auto_now_add=True)
    ultima_fecha_de_edicion = models.DateTimeField(auto_now=True)
    order = models.SmallIntegerField(default=0, verbose_name="Orden")
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

    def save(self, *args, **kwargs):
        if not self.pk:  # New instance, so calculate initial values
            if not self.monto_mas_interes:
                self.monto_mas_interes = self.monto * 1.20  # Assuming 20% interest
            if not self.couta_diaria:
                self.couta_diaria = self.monto_mas_interes / 20  # Assuming 20 days installment
            self.saldo = self.monto_mas_interes  # Set initial saldo to the total amount due

        super().save(*args, **kwargs)  # Save the instance first

        if self.pk:  # Only update saldo if instance is saved
            self.update_saldo()
            
    # ESTO ES PARA QUE EL SALDO SE ACTUALICE SI BORRAN UN ABONO SE SUME AL SALDO
    def update_saldo(self):
        total_payments = sum(payment.payment_amount for payment in self.get_payments())
        self.saldo = self.monto_mas_interes - total_payments
        # Save the updated saldo separately to avoid recursion
        if self.pk:  # Ensure the instance is saved
            super().save(update_fields=['saldo'])
    ###############################################################################
    
    
    # DESDE AQUI ESTO LO AGREGAMOS PARA PODER VER EL HISTORIAL DE PAGOS DE CADA CLIENTE 
    def get_payments(self):
        return Payment.objects.filter(cliente=self)
    ###########################################################################################3
    
    
    # ESTO ES PARA QUE SE PONGAN EN ROJO SI NO TERMINAN DE PAGAR EN 20 DIAS, ESTO VA ACOMPANADO DE UN METODO EN admin.py
    def is_overdue(self):
        last_payment_date = self.payment_set.order_by('-payment_date').values_list('payment_date', flat=True).first()
        if not last_payment_date:
            return False
        overdue_threshold = last_payment_date + timedelta(days=20)
        return timezone.now() > overdue_threshold
    #################################################################################
    
    
    # ESTO PARA VER CUANTOS DIAS TIENE ATRASADO EL CLIENTE 
    def days_since_last_payment(self):
        last_payment_date = self.payment_set.order_by('-payment_date').values_list('payment_date', flat=True).first()
        if not last_payment_date:
            return None
        days_since_payment = (timezone.now() - last_payment_date).days
        return days_since_payment
    ########################################################################################
    
    
    #ESTE ES PARTE DEL METODO PARA QUE SI EL CLIENTE LLEGA A 0 DESAPAREZCA DE LA LISTA Y SE VAYA A LISTA DE CANCELADOS
    @classmethod
    def with_zero_saldo(cls):
        return cls.objects.filter(saldo=0) 
    ######ESTO VA ACOMPANADO DEL METODO DE MOSTRAR LOS CLIENTES EN views.py Y un formulario en la vista que estoy mostrando el boton de ver lista de clientes cancelados, SIN ESE FORM NO FUNCIONA ESTE METODO
    
    
    class Meta:
        verbose_name = "Tu cliente"
        verbose_name_plural = "Tus Clientes"
        ordering = ['order']
        
class Payment(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Payment of {self.payment_amount} made on {self.payment_date}"
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['payment_date']

class AgregarGasto(models.Model):
    descripcion_gasto = models.CharField(max_length=200)
    monto_gasto = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.descripcion_gasto} - ${self.monto_gasto}"
    
    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['created_at']

class AgregarBase(models.Model):
    descripcion_base = models.CharField(max_length=200)
    monto_base = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        # Concatenate fields into a single string
        return f"{self.descripcion_base} - ${self.monto_base} on {self.created_at}"
    
    class Meta:
        verbose_name = "Base"
        verbose_name_plural = "Historial de Bases"
        ordering = ['created_at']
