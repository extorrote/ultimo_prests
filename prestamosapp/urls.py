
from django.urls import path,include
from prestamosapp import views
from django.contrib import admin
from django.conf import settings#ESTO ES PARA PODER VISUALIZAR LAS FOTOS
from django.conf.urls.static import static #ESTO ES PARA PODER VISUALIZAR LAS FOTOS

app_name='prestamosapp'
urlpatterns = [
    path('admin/', admin.site.urls), 
    path('clientes-saldo-cero/', views.clientes_con_saldo_cero, name='clientes_con_saldo_cero'),
    path('inicio/', views.inicio, name='inicio'),
    path('', views.cliente_list, name='cliente_list'),
    path('cliente_list/', views.cliente_list, name='cliente_list'),
    path('agregar_cliente/', views.add_cliente, name='agregar_cliente'),
    path('borrar_cliente<int:cliente_id>/', views.borrar_cliente, name='borrar_cliente'),
    path('informacion_cliente/<int:pk>/', views.cliente_full_info, name='informacion_cliente'),
    
    
    path('clientes/<int:cliente_id>/add_payment/', views.add_payment, name='add_payment'),
    path('cobro_del_dia/', views.cobro_del_dia, name='cobro_del_dia'),
    path('historia_cobro/', views.historial_cobro, name='historia_cobro'),
    

    
    path('clientes/<int:cliente_id>/edit/', views.edit_cliente, name='edit_cliente'),
    path('clientes/<int:cliente_id>/', views.historial_de_pagos, name='client_detail'),
    path('clientes/<int:cliente_id>/delete_payment/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    
    path('agregar_gasto/', views.agregar_gasto, name='agregar_gasto'),
    path('lista_gastos_del_dia/', views.lista_gastos_del_dia, name='lista_gastos_del_dia'),
    path('gastos_semanales/', views.lista_gastos_de_la_semana, name='gastos_semanales'),
    path('gastos-del-mes/', views.lista_gastos_del_mes, name='gastos_del_mes'),
    path('todos-los-gastos/', views.lista_todos_los_gastos, name='todos_los_gastos'),
    
    path('agregar_base/', views.agregar_base, name='agregar_base'),
    path('historial_base/', views.historial_base, name='historial_base'),
    
    
    # BUSCADOR 
    path('search/', views.ClienteSearchView.as_view(), name='cliente-search'),
    
    path('liquidacion-del-dia/', views.liquidacion_del_Dia, name='liquidacion_del_dia'),
    path('liquidacion-total/', views.liquidacion_total, name='liquidacion_total'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #ESTO ES PARA PODER VISUALIZAR LAS FOTOS