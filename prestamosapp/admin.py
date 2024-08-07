from django.contrib import admin
from prestamosapp.models import Cliente, Payment, AgregarGasto, AgregarBase

# ESTO ES PARA QUE EL SISTEMA PINTE DE ROJO CUANDO UN CLIENTE NO PAGA A TIEMPO
class OverdueFilter(admin.SimpleListFilter):
    title = 'Overdue Status'
    parameter_name = 'is_overdue'

    def lookups(self, request, model_admin):
        return [
            ('overdue', 'Overdue'),
            ('not_overdue', 'Not Overdue'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'overdue':
            return queryset.filter(id__in=[
                cliente.id for cliente in queryset
                if cliente.is_overdue()
            ])
        if self.value() == 'not_overdue':
            return queryset.exclude(id__in=[
                cliente.id for cliente in queryset
                if cliente.is_overdue()
            ])
        return queryset

class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellidos', 'monto', 'saldo', 'fecha_de_creacion']
    list_filter = [OverdueFilter]  # Use the custom filter class here
    search_fields = ['nombre', 'apellidos']
    

admin.site.register(Cliente, ClienteAdmin)



# Define a custom admin interface for Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'payment_amount', 'payment_date')
    search_fields = ('cliente__nombre', 'cliente__apellidos', 'payment_amount')
    list_filter = ('payment_date',)
    ordering = ('-payment_date',)

# Define a custom admin interface for AgregarGasto
@admin.register(AgregarGasto)
class AgregarGastoAdmin(admin.ModelAdmin):
    list_display = ('descripcion_gasto', 'monto_gasto', 'created_at')
    search_fields = ('descripcion_gasto',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Define a custom admin interface for AgregarBase
@admin.register(AgregarBase)
class AgregarBaseAdmin(admin.ModelAdmin):
    list_display = ('descripcion_base', 'monto_base', 'created_at')
    search_fields = ('descripcion_base',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
    

