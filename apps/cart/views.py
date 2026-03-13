from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Cart, CartItem
from apps.catalog.models import Product

def get_or_create_cart(request):
    """Única función para obtener o crear el carrito - USAR EN TODAS PARTES"""
    print(f"\n🔧 get_or_create_cart - Usuario: {request.user}")
    
    if request.user.is_authenticated:
        # Usuario autenticado: buscar o crear carrito por usuario
        cart, created = Cart.objects.get_or_create(user=request.user)
        print(f"   - Usuario autenticado: {request.user.email}")
        print(f"   - Carrito {'creado' if created else 'existente'}: {cart.id}")
        print(f"   - Items en carrito: {cart.items.count()}")
        
        # Transferir items de carrito anónimo si existe
        session_key = request.session.session_key
        if session_key:
            anonymous_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if anonymous_cart and anonymous_cart.items.exists():
                print(f"   - Transfiriendo {anonymous_cart.items.count()} items del carrito anónimo")
                for item in anonymous_cart.items.all():
                    existing_item = cart.items.filter(product=item.product).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.cart = cart
                        item.save()
                anonymous_cart.delete()
                print(f"   - Items después de transferir: {cart.items.count()}")
    else:
        # Usuario anónimo: buscar o crear carrito por session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            print(f"   - Nueva session_key creada: {session_key}")
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            user__isnull=True,
            defaults={'user': None}
        )
        print(f"   - Carrito anónimo {'creado' if created else 'existente'}: {cart.id}")
        print(f"   - Items en carrito: {cart.items.count()}")
    
    return cart

def cart_detail(request):
    """Vista para mostrar el contenido del carrito"""
    print("\n=== ENTRANDO A CART_DETAIL ===")
    
    # USAR LA MISMA FUNCIÓN QUE EN CART_ADD
    cart = get_or_create_cart(request)
    
    print(f"📦 Carrito obtenido: ID {cart.id}")
    print(f"   - Items en carrito: {cart.items.count()}")
    
    # Si no hay items, mostrar carrito vacío
    if not cart.items.exists():
        print("🟡 Carrito sin items")
        context = {
            'cart': None,
            'subtotal': Decimal('0'),
            'shipping': Decimal('0'),
            'tax': Decimal('0'),
            'total': Decimal('0'),
            'free_shipping_threshold': Decimal('500'),
            'remaining_for_free_shipping': Decimal('500'),
        }
        return render(request, 'cart/detail.html', context)
    
    # Mostrar items para debug
    for item in cart.items.all():
        print(f"      - {item.product.name}: {item.quantity}")
    
    # Calcular totales
    subtotal = cart.get_total()
    
    SHIPPING_RATE = Decimal('0.05')
    TAX_RATE = Decimal('0.16')
    FREE_SHIPPING_THRESHOLD = Decimal('500')
    
    if subtotal < FREE_SHIPPING_THRESHOLD:
        shipping = subtotal * SHIPPING_RATE
    else:
        shipping = Decimal('0')
    
    tax = subtotal * TAX_RATE
    total = subtotal + shipping + tax
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'free_shipping_threshold': FREE_SHIPPING_THRESHOLD,
        'remaining_for_free_shipping': max(Decimal('0'), FREE_SHIPPING_THRESHOLD - subtotal),
    }
    return render(request, 'cart/detail.html', context)

@require_POST
def cart_add(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id, is_available=True)
        quantity = int(request.POST.get('quantity', 1))
        cart = get_or_create_cart(request)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': 0}
        )
        
        new_quantity = cart_item.quantity + quantity
        
        if new_quantity <= product.stock:
            cart_item.quantity = new_quantity
            cart_item.save()
            message = f'✓ {product.name} actualizado'
        else:
            return JsonResponse({
                'success': False,
                'message': f'Stock insuficiente (Máx: {product.stock})'
            }, status=400)

        # CÁLCULO SEGURO DEL CONTEO TOTAL
        # Sumamos las cantidades de todos los items
        total_quantity = sum(item.quantity for item in cart.items.all())
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total': float(cart.get_total()),
                'cart_count': total_quantity, # <--- El numerito que buscamos
                'message': message
            })
        
        messages.success(request, message)
        return redirect('cart:cart_detail')
        
    except Exception as e:
        # Esto nos dirá exactamente qué falló en la consola de Django
        print(f"DEBUG ERROR: {str(e)}") 
        return JsonResponse({
            'success': False,
            'message': 'Error interno en el servidor'
        }, status=500)

@require_POST
def cart_remove(request, product_id):
    """Vista para eliminar productos del carrito"""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    if cart:
        cart_item = cart.items.filter(product=product).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f'✓ {product.name} eliminado del carrito')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.get_total()) if cart else 0,
            'cart_count': cart.items.count() if cart else 0
        })
    
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    """Vista para actualizar cantidad de productos"""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = get_or_create_cart(request)
    
    if cart:
        cart_item = cart.items.filter(product=product).first()
        if cart_item:
            if quantity > 0 and quantity <= product.stock:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f'✓ Cantidad actualizada: {quantity} x {product.name}')
            elif quantity > product.stock:
                messages.error(request, f'❌ Stock insuficiente. Stock disponible: {product.stock}')
            else:
                cart_item.delete()
                messages.success(request, f'✓ {product.name} eliminado del carrito')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_total': float(cart_item.get_total()) if cart_item else 0,
            'cart_total': float(cart.get_total()) if cart else 0,
            'cart_count': cart.items.count() if cart else 0
        })
    
    return redirect('cart:cart_detail')

def cart_count(request):
    """Vista para obtener el conteo total de piezas del carrito"""
    cart = get_or_create_cart(request)
    # Cambiamos .count() por la suma de cantidades
    count = sum(item.quantity for item in cart.items.all()) if cart else 0
    return JsonResponse({'count': count})