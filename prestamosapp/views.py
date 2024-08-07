from django.shortcuts import render, redirect,get_object_or_404
from prestamosapp.models import Cliente,Payment
from prestamosapp.forms import PaymentForm
from prestamosapp.forms import ClienteForm
from django.utils import timezone
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def add_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save(commit=False)
            # Ensure monto_mas_interes and couta_diaria are calculated
            if not cliente.monto_mas_interes:
                cliente.monto_mas_interes = cliente.monto * 1.20  # Example calculation for 20% interest
            cliente.couta_diaria = cliente.monto_mas_interes / 20  # Example calculation for 20 days
            cliente.save()
            return redirect('prestamosapp:cliente_list')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
    }
    return render(request, 'add_cliente.html', context)

###################################################
#ESTO LO ESTOY HACIENDO PARA AL DARLE CLIC A TODA LA INFO DEL CLIENTE SE ME ABRA EN UNA NUEVA TEMPLATE 
def cliente_full_info(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    days_since_last_payment = cliente.days_since_last_payment()
    return render(request, 'detalles_cliente.html', {
        'cliente': cliente,
        'days_since_last_payment': days_since_last_payment
    })



def cliente_list(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        payment_amount = request.POST.get('payment_amount')#ESTE ES EL FORM DE LOS PAGOS
        move_to_saldo_cero = request.POST.get('move_to_saldo_cero')#ESTE ES EL FORM DE SACAR LOS CLIENTES EN 0

        if move_to_saldo_cero:
            # Move all clients with saldo cero to a separate view
            return redirect('prestamosapp:clientes_con_saldo_cero')

        if cliente_id:
            cliente = get_object_or_404(Cliente, id=cliente_id)

            if payment_amount:
                # Handle payment processing
                payment_date = timezone.now()
                payment = Payment(cliente=cliente, payment_amount=payment_amount, payment_date=payment_date)
                payment.save()
                cliente.update_saldo()

            if move_to_saldo_cero:
                # Move client to saldo cero list
                cliente.saldo = 0
                cliente.save()
                return redirect('prestamosapp:cliente_list')  # Redirect to refresh the list

    # Query all clients
    clientes = Cliente.objects.all().order_by('order')
    clientes_con_saldo_cero = clientes.filter(saldo=0)
    clientes_con_saldo = clientes.exclude(saldo=0)
    total_pending = clientes_con_saldo.aggregate(total_saldo=Sum('saldo'))['total_saldo'] or 0
    
    context = {
        'clientes': clientes_con_saldo,  # Only include clients with saldo > 0
        'form': PaymentForm(),
        'total_pending': total_pending,
    }
    
    return render(request, 'cliente_list.html', context)
    

def clientes_con_saldo_cero(request):
    clientes_saldo_cero = Cliente.objects.filter(saldo=0).order_by('order')
    context = {
        'clientes': clientes_saldo_cero,
    }
    return render(request, 'clientes_con_saldo_cero.html', context)




def add_payment(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_amount = form.cleaned_data['payment_amount']
            
            # Set payment_date to current datetime
            payment_date = timezone.now()
            
            payment = Payment(cliente=cliente, payment_amount=payment_amount, payment_date=payment_date)
            payment.save()
            
            # Update cliente's saldo
            cliente.update_saldo()
            
            return redirect('prestamosapp:cliente_list')
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'cliente': cliente,
        'payments': cliente.get_payments(),
    }
    return render(request, 'cliente_list.html', context)



import pytz #ESTO LO TUBE QUE IMPORTAR PARA PODER PONER LA HORA DE MEXICO PORQUE NO ME LA ESTABA SACANDO CORRECTA Y TAMBIEN TUBE QUE CAMBIAR LA TIME_ZONE EN settings.py

#ESTO ES PARA VER LO QUE SE COBRO EN EL DIA 
def cobro_del_dia(request):
    mexico_tz = pytz.timezone('America/Mexico_City')
    now = timezone.now().astimezone(mexico_tz)
    today = now.date()
    
    start_of_day = mexico_tz.localize(timezone.datetime.combine(today, timezone.datetime.min.time()))
    end_of_day = mexico_tz.localize(timezone.datetime.combine(today, timezone.datetime.max.time()))

    payments_today = Payment.objects.filter(payment_date__range=(start_of_day, end_of_day))
    total_payments_today = payments_today.aggregate(total=Sum('payment_amount'))['total'] or 0

    context = {
        'total_payments_today': total_payments_today,
        'date': now.strftime("%d %B %Y"),
        'start_of_day': start_of_day.strftime("%d %B %Y %I:%M %p"),
        'end_of_day': end_of_day.strftime("%d %B %Y %I:%M %p")
    }

    return render(request, 'daily_payments_summary.html', context)

def historial_cobro(request):
    # Define the timezone
    mexico_tz = pytz.timezone('America/Mexico_City')
    now = timezone.now().astimezone(mexico_tz).date()
    
    # Get the earliest payment date from the Payment model
    earliest_payment = Payment.objects.order_by('payment_date').first()
    
    if not earliest_payment:
        # If there are no payments, return a message or handle this case as needed
        return render(request, 'daily_payments_summary.html', {'error': 'No payments found.'})
    
    start_date = earliest_payment.payment_date.date()
    
    # Generate a list of dates from start_date to today
    days_range = [start_date + timedelta(days=x) for x in range((now - start_date).days + 1)]

    daily_payments = []

    for day in days_range:
        start_of_day = mexico_tz.localize(timezone.datetime.combine(day, timezone.datetime.min.time()))
        end_of_day = mexico_tz.localize(timezone.datetime.combine(day, timezone.datetime.max.time()))

        payments_day = Payment.objects.filter(payment_date__range=(start_of_day, end_of_day))
        total_payments_day = payments_day.aggregate(total=Sum('payment_amount'))['total'] or 0

        daily_payments.append({
            'date': start_of_day.strftime("%d %B %Y"),
            'total_payments': total_payments_day
        })

    context = {
        'daily_payments': daily_payments,
    }
    return render(request, 'historial_de_cobros_diarios.html', context)



#METODO PARA BORRAR PAGO Y QUE SE REGRESE AL SALDO DEL CLIENTE 
def delete_payment(request, cliente_id, payment_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    payment = get_object_or_404(Payment, id=payment_id)

    # Save the payment amount to add back to the saldo
    deleted_payment_amount = payment.payment_amount
    
    # Delete the payment
    payment.delete()

    # Update cliente's saldo by adding back the deleted payment amount
    cliente.saldo += deleted_payment_amount
    cliente.save()

    return redirect('prestamosapp:cliente_list')



def edit_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('prestamosapp:cliente_list')  # Redirect to client list or detail view
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
    }
    return render(request, 'edit_cliente.html', context)


#ESTO ES PARA VER LO QUE SE COBRO EN EL DIA 



#ESTO ES PARA VER LOS PAGOS QUE HA HECHO CADA CLIENTE Y LA FECHA, PARA ESTO DEBI CREAR EL MODELO payment
def historial_de_pagos(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    payments = Payment.objects.filter(cliente=cliente).order_by('-payment_date')
    
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        if payment_id:
            payment = get_object_or_404(Payment, id=payment_id)
            # Get payment amount to add back to cliente's saldo
            payment_amount = payment.payment_amount
            # Delete the payment
            payment.delete()
            # Update cliente's saldo after deleting payment
            cliente.update_saldo()
            # Redirect to prevent re-submitting the form on refresh
            return redirect('prestamosapp:client_detail', cliente_id=cliente_id)
    
    context = {
        'cliente': cliente,
        'payments': payments,
    }
    return render(request, 'historial_de_pagos.html', context)

#SI EL USUARIO BORRA UN CLIENTE Y EL CLIENTE TIENE SALDO EL SALDO SE VA IR A LA BASE, PARA ESTO TUBE QUE AGREGAR UN METODO EN EL MODELO TAMBIEN
def borrar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    if request.method == 'POST':
        # Delete the cliente and redirect to cliente list or another appropriate page
        cliente.delete()
        return redirect('prestamosapp:cliente_list')  # Redirect to your client list URL name
    
    context = {
        'cliente': cliente,
    }
    return render(request, 'delete_cliente.html', context)


from paquete2.forms import AgregarGastoForm,AgregarBaseForm
from paquete2.models import AgregarGasto,AgregarBase

def agregar_gasto(request):
    if request.method == 'POST':
        form = AgregarGastoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('prestamosapp:lista_gastos_del_dia')  # Redirect to a page listing all gastos
    else:
        form = AgregarGastoForm()
    
    return render(request, 'agregar_gasto.html', {'form': form})





from django.utils import timezone #ESTE LO TUBE QUE IMPORTAR PARA SACAR LOS GASTOS DEL DIA SEMANA Y MES
from django.db.models import Sum #ESTE LO TUBE QUE IMPORTAR PARA SACAR LOS GASTOS DEL DIA
from datetime import timedelta #ESTE LO OCUPE A PARTIR DE MOSTRAR LOS GASTOS DE 7 DIAS

def lista_gastos_del_dia(request):
    today = timezone.localdate()  # Get the local date considering time zones
    gastos = AgregarGasto.objects.filter(created_at__date=today)
    total = gastos.aggregate(Sum('monto_gasto'))['monto_gasto__sum']

    # Debugging
    print(f"Today's date: {today}")
    print(f"Gastos: {gastos}")
    print(f"Total amount: {total}")

    return render(request, 'lista_gastos_del_dia.html', {
        'gastos': gastos,
        'total': total
    })



def lista_todos_los_gastos(request):
    # Retrieve all expenses
    gastos = AgregarGasto.objects.all()
    # Calculate the total amount
    total = gastos.aggregate(Sum('monto_gasto'))['monto_gasto__sum']

    return render(request, 'lista_todos_los_gastos.html', {
        'gastos': gastos,
        'total': total
    })
    
    

def lista_gastos_de_la_semana(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
    end_of_week = start_of_week + timedelta(days=6)  # Sunday of the current week

    gastos = AgregarGasto.objects.filter(created_at__date__range=[start_of_week, end_of_week])
    total = gastos.aggregate(Sum('monto_gasto'))['monto_gasto__sum']

    return render(request, 'lista_gastos_de_la_semana.html', {
        'gastos': gastos,
        'total': total
    })
    

    

def lista_gastos_del_mes(request):
    today = timezone.now().date()
    # Calculate the first day of the current month
    start_of_month = today.replace(day=1)
    # Calculate the last day of the current month
    end_of_month = (start_of_month.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1))

    gastos = AgregarGasto.objects.filter(created_at__date__range=[start_of_month, end_of_month])
    total = gastos.aggregate(Sum('monto_gasto'))['monto_gasto__sum']

    return render(request, 'lista_gastos_del_mes.html', {
        'gastos': gastos,
        'total': total
    })

def agregar_base(request):
    if request.method == 'POST':
        form = AgregarBaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('prestamosapp:historial_base')  # Redirect to a page listing all gastos
    else:
        form = AgregarBaseForm()
    
    return render(request, 'agregar_base.html', {'form': form})




def historial_base(request):
    base= AgregarBase.objects.all()
    return render(request, 'historial_base.html', {'base': base})





def liquidacion_del_Dia(request):
    today = timezone.localdate()  # Get the local date considering time zones

    # Fetch the last base amount added
    last_base_entry = AgregarBase.objects.latest('created_at')#EXISTE : first_base_entry = AgregarBase.objects.earliest('created_at')
    base_entregada = last_base_entry.monto_base if last_base_entry else 0

    # Fetch all payments made today
    cobro = Payment.objects.filter(payment_date__date=today).aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0

    # Fetch all prestamos (loans) recorded today
    prestamos = Cliente.objects.filter(fecha_de_creacion__date=today).aggregate(Sum('monto'))['monto__sum'] or 0

    # Fetch all gastos recorded today
    gastos = AgregarGasto.objects.filter(created_at__date=today).aggregate(Sum('monto_gasto'))['monto_gasto__sum'] or 0

    # Calculate total base amount
    base_total = base_entregada + cobro - prestamos - gastos

    context = {
        'base_entregada': base_entregada,
        'cobro': cobro,
        'prestamos': prestamos,
        'gastos': gastos,
        'base_total': base_total,
    }

    return render(request, 'liquidacion_del_dia.html', context)


def liquidacion_total(request):
    # Get the oldest base entry
    try:
        first_base_entry = AgregarBase.objects.order_by('created_at').first()
        if first_base_entry:
            start_date = first_base_entry.created_at.date()
            base_entregada = first_base_entry.monto_base
        else:
            # Handle case where there are no base entries
            start_date = timezone.localdate()
            base_entregada = 0
    except AgregarBase.DoesNotExist:
        # Handle case where there are no base entries
        start_date = timezone.localdate()
        base_entregada = 0

    # Aggregate data since the start date
    cobro_total = Payment.objects.filter(payment_date__date__gte=start_date).aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0

    prestamos_total = Cliente.objects.filter(fecha_de_creacion__date__gte=start_date).aggregate(Sum('monto'))['monto__sum'] or 0

    gastos_total = AgregarGasto.objects.filter(created_at__date__gte=start_date).aggregate(Sum('monto_gasto'))['monto_gasto__sum'] or 0

    # Calculate total base amount
    base_total = base_entregada + cobro_total - prestamos_total - gastos_total

    context = {
        'base_entregada': base_entregada,
        'cobro_total': cobro_total,
        'prestamos_total': prestamos_total,
        'gastos_total': gastos_total,
        'base_total': base_total,
        'start_date': start_date,
    }
    return render(request, 'liquidacion_total.html', context)


from rest_framework import generics #ESTO ES PARA EL METODO DEL BUSCADOR EN TIEMPO REAL 
from prestamosapp.serializers import ClienteSerializer #ESTO ES PARA EL METODO DEL BUSCADOR EN TIEMPO REAL
from rest_framework.response import Response #ESTO ES PARA EL METODO DEL BUSCADOR EN TIEMPO REAL ESTE HACE QUE EL CLIENTE SE VENGA DE PRIMERA FILA CUANDO EL USUARIO ESTA BUSCANDO UN NOMBRE



class ClienteSearchView(generics.ListAPIView):
    serializer_class = ClienteSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Cliente.objects.filter(nombre__icontains=query)
        return Cliente.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        first_client = data[0] if data else None
        return Response({
            'results': data,
            'first_client': first_client
        })
        

def inicio(request):
    return render(request,'index.html')    

def login_user(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')#ESTO ES LO QUE LE HE PUESTO EN EL NAME EN EL CAMPO DEL FORMULARIO
        user=authenticate(request,username=username,password=password)#KEYBOL ARGUMENT ES CUANDO VA UN LA PRIMERA ES LA KEIBOLNAME  NOMBRE=NOMBRE LA SEGUNDA ES LA VARIABLE QUE ESTA RECIBIENDO
        if user is not None:
            login(request,user)
            return redirect('prestamosapp:cliente_list')
        else:
            messages.warning (request,'No te has identificado Correctamente')   


    return render (request,'login.html',{'title':'identificate'})


def logout_user(request):
    logout(request)
    return redirect ('prestamosapp:cliente_list')


