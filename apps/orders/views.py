import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
import logging
from django.urls import reverse
import paypalrestsdk
from decimal import Decimal
from .models import Order, OrderItem, OrderHistory
from apps.cart.models import Cart
from .utils import calculate_delivery_date

logger = logging.getLogger(__name__)


@login_required
def order_list(request):
    """Vista para listar las órdenes del usuario"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    """Vista para ver detalle de una orden"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def checkout_view(request):
    """Vista de checkout/pago con selección de método de entrega"""
    # Obtener el carrito del usuario
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart or not cart.items.exists():
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('catalog:catalog')
    
    # Definir constantes
    HOME_DELIVERY_COST = Decimal('50')
    
    # Calcular totales base
    subtotal = cart.get_total()
    
    if request.method == 'POST':
        delivery_method = request.POST.get('delivery_method')
        pickup_point = request.POST.get('pickup_point')
        
        # Validar método de entrega
        if not delivery_method:
            messages.error(request, 'Debes seleccionar un método de entrega')
            return redirect('orders:checkout')
        
        # Validar punto de recogida si aplica
        if delivery_method == 'pickup' and not pickup_point:
            messages.error(request, 'Debes seleccionar un punto de recogida')
            return redirect('orders:checkout')
        
        # ===== NUEVA VALIDACIÓN PARA FECHA DE RECOGIDA =====
        if delivery_method == 'pickup' and pickup_point == 'segundo_lugar':
            pickup_date_str = request.POST.get('pickup_date')
            
            if not pickup_date_str:
                messages.error(request, 'Debes seleccionar una fecha de recogida')
                return redirect('orders:checkout')
            
            # Validar la fecha
            from datetime import datetime
            from django.utils import timezone
            
            try:
                pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
                today = timezone.now().date()
                current_time = timezone.now()
                current_hour = current_time.hour
                
                # Validar que no sea fecha pasada
                if pickup_date < today:
                    messages.error(request, 'No puedes seleccionar una fecha pasada')
                    return redirect('orders:checkout')
                
                # Validar que no sea domingo
                if pickup_date.weekday() == 6:  # 6 = domingo
                    messages.error(request, 'No hay recogidas los domingos')
                    return redirect('orders:checkout')
                
                # Si es hoy, validar que sea antes de las 5 PM
                if pickup_date == today and current_hour >= 17:
                    messages.error(request, 'Ya no puedes seleccionar hoy para recoger (después de las 5:00 PM)')
                    return redirect('orders:checkout')
                    
            except ValueError:
                messages.error(request, 'Fecha inválida')
                return redirect('orders:checkout')
            
              # ===== VALIDACIÓN PARA PUNTO 1 (MERCADO - SOLO SÁBADOS) =====
        if delivery_method == 'pickup' and pickup_point == 'mercado':
            from datetime import datetime
            from django.utils import timezone
            
            today = timezone.now().date()
            current_hour = timezone.now().hour
            
            # Solo sábados
            if today.weekday() != 5:  # 5 = sábado
                messages.error(request, 'El punto 1 solo está disponible los sábados')
                return redirect('orders:checkout')
            
            # Horario de 8 AM a 1 PM
            if current_hour < 8 or current_hour >= 13:
                messages.error(request, 'El punto 1 solo está disponible de 8:00 AM a 1:00 PM los sábados')
                return redirect('orders:checkout')
        
        # Calcular costos según método de entrega
        if delivery_method == 'home_delivery':
            shipping_cost = HOME_DELIVERY_COST
            estimated_date = calculate_delivery_date()
            delivery_time = '9:00 AM - 6:00 PM'
            pickup_point = None
            
            # Validar campos de dirección para Mérida
            colonia = request.POST.get('colonia', '').strip()
            calle = request.POST.get('calle', '').strip()
            numero_casa = request.POST.get('numero_casa', '').strip()
            entre_calles = request.POST.get('entre_calles', '').strip()
            referencias = request.POST.get('referencias', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            if not all([colonia, calle, phone]):
                messages.error(request, 'La colonia, calle y teléfono son obligatorios')
                return redirect('orders:checkout')
            
            # Validar teléfono
            phone_clean = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '')
            if len(phone_clean) < 10:
                messages.error(request, 'Ingresa un teléfono válido (mínimo 10 dígitos)')
                return redirect('orders:checkout')
            
            # Construir dirección
            shipping_address = f"Calle {calle}"
            if numero_casa:
                shipping_address += f" #{numero_casa}"
            shipping_address += f", Col. {colonia}"
            if entre_calles:
                shipping_address += f" (entre {entre_calles})"
            if referencias:
                shipping_address += f". Ref: {referencias}"
            
            # Guardar en perfil
            request.user.colonia = colonia
            request.user.calle = calle
            request.user.numero_casa = numero_casa
            request.user.entre_calles = entre_calles
            request.user.referencias = referencias
            request.user.phone = phone
            request.user.save()
            
            city = 'Mérida'
            state = 'Yucatán'
            postal_code = ''
            
        else:  # pickup
            shipping_cost = Decimal('0')
            estimated_date = None
            delivery_time = 'Horario de recogida'
            shipping_address = ''
            city = ''
            state = ''
            postal_code = ''
            phone = request.POST.get('phone', '')
        
        # Calcular total
        total = subtotal + shipping_cost
        
        # Crear la orden
        order = Order.objects.create(
            user=request.user,
            delivery_method=delivery_method,
            pickup_point=pickup_point,
            pickup_date=request.POST.get('pickup_date') if delivery_method == 'pickup' and pickup_point == 'segundo_lugar' else None,  # NUEVO
            estimated_delivery_date=estimated_date,
            delivery_time_slot=delivery_time,
            shipping_address=shipping_address,
            shipping_city=city if delivery_method == 'home_delivery' else '',
            shipping_state=state if delivery_method == 'home_delivery' else '',
            shipping_postal_code=postal_code if delivery_method == 'home_delivery' else '',
            shipping_phone=phone,
            payment_method='paypal',
            payment_status='pending',
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=Decimal('0'),
            total=total,
            notes=request.POST.get('notes', '')
        )
        
        # Crear items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                product_name=item.product.name
            )
        
        # Crear historial
        OrderHistory.objects.create(
            order=order,
            status='pending',
            notes=f'Orden creada - Método: {order.get_delivery_method_display()}',
            created_by=request.user
        )
        
        # Vaciar carrito
        cart.items.all().delete()
        
        messages.success(request, f'¡Pedido #{order.order_number} creado! Redirigiendo a PayPal...')
        request.session['cart_emptied'] = True
        
        # ===== REDIRECCIÓN A PAYPAL =====
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": request.build_absolute_uri(reverse('orders:payment_done')),
                    "cancel_url": request.build_absolute_uri(reverse('orders:payment_cancelled'))
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"Pedido #{order.order_number}",
                            "sku": order.order_number,
                            "price": str(order.total),
                            "currency": "MXN",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(order.total),
                        "currency": "MXN"
                    },
                    "description": f"Pago de pedido #{order.order_number} - Flores Teya"
                }]
            })
            
            if payment.create():
                order.paypal_order_id = payment.id
                order.save()
                
                # Buscar URL de aprobación
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        return redirect(approval_url)
                
                # Si no encuentra la URL
                messages.error(request, 'No se pudo obtener la URL de pago de PayPal')
                return redirect('orders:order_detail', order_id=order.id)
            else:
                logger.error(f"Error creando pago PayPal: {payment.error}")
                messages.error(request, 'Error al conectar con PayPal. Intenta nuevamente.')
                return redirect('orders:order_detail', order_id=order.id)
                
        except Exception as e:
            logger.error(f"Error en checkout_view - PayPal: {e}")
            messages.error(request, f'Error al procesar el pago: {str(e)}')
            return redirect('orders:order_detail', order_id=order.id)
    
    # ===== MÉTODO GET =====
    estimated_delivery = calculate_delivery_date()
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': Decimal('0'),
        'total': subtotal,
        'home_delivery_cost': HOME_DELIVERY_COST,
        'estimated_delivery': estimated_delivery,
    }
    return render(request, 'orders/checkout.html', context)
    
    # Para GET: calcular fechas de ejemplo para mostrar
    estimated_delivery = calculate_delivery_date()
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': Decimal('0'),
        'total': subtotal,
        'home_delivery_cost': HOME_DELIVERY_COST,
        'estimated_delivery': estimated_delivery,
    }
    return render(request, 'orders/checkout.html', context)

# Agrega esta función de validación
def validate_pickup_date(pickup_date_str, pickup_point):
    """
    Valida que la fecha de recogida sea válida según las reglas de negocio
    """
    if not pickup_date_str or pickup_point != 'segundo_lugar':
        return True, None
    
    try:
        # Convertir string a fecha
        pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
        today = timezone.now().date()
        current_time = timezone.now()
        current_hour = current_time.hour
        
        # Verificar que no sea una fecha pasada
        if pickup_date < today:
            return False, "No puedes seleccionar una fecha pasada"
        
        # Si es hoy, verificar que sea antes de las 5 PM
        if pickup_date == today:
            if current_hour >= 17:  # 5:00 PM
                return False, "Ya no puedes seleccionar hoy para recoger (después de las 5:00 PM)"
        
        # Verificar que no sea domingo
        day_of_week = pickup_date.weekday()  # 0=lunes, 6=domingo
        if day_of_week == 6:  # Domingo
            return False, "No hay recogidas los domingos"
        
        return True, None
        
    except Exception as e:
        return False, f"Error en la fecha: {str(e)}"

@login_required
def create_paypal_payment(request, order_id):
    """Crea un pago en PayPal para la orden"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('orders:payment_done')),
                "cancel_url": request.build_absolute_uri(reverse('orders:payment_cancelled'))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Pedido #{order.order_number}",
                        "sku": order.order_number,
                        "price": str(order.total),
                        "currency": "MXN",
                        "quantity": 1
                    }]
                },
                "amount": {"total": str(order.total), "currency": "MXN"},
                "description": f"Pago de pedido #{order.order_number}"
            }]
        })
        
        if payment.create():
            order.paypal_order_id = payment.id
            order.save()
            
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
            
            messages.error(request, 'No se pudo obtener la URL de pago')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Error al crear el pago en PayPal')
            return redirect('orders:order_detail', order_id=order.id)
            
    except Exception as e:
        logger.error(f"Error en create_paypal_payment: {e}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('orders:order_detail', order_id=order.id)

@login_required
def payment_done(request):
    """Vista cuando el pago se completa exitosamente"""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        messages.error(request, 'Error en el pago: información incompleta')
        return redirect('orders:order_list')
    
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            order = Order.objects.get(paypal_order_id=payment_id)
            order.payment_status = 'paid'
            order.status = 'processing'
            order.payment_reference = payment_id
            order.save()
            
            OrderHistory.objects.create(
                order=order,
                status='processing',
                notes=f'Pago completado con PayPal. ID: {payment_id}',
                created_by=request.user
            )
            
            messages.success(request, '¡Pago completado exitosamente!')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Error al ejecutar el pago')
            return redirect('orders:order_list')
            
    except Order.DoesNotExist:
        messages.error(request, 'No se encontró la orden asociada')
        return redirect('orders:order_list')
    except Exception as e:
        logger.error(f"Error en payment_done: {e}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('orders:order_list')

def payment_cancelled(request):
    """Vista cuando el usuario cancela el pago"""
    messages.warning(request, 'Has cancelado el pago. Puedes intentar nuevamente cuando quieras.')
    return redirect('orders:order_list')