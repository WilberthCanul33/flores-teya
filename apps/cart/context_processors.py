from .models import Cart

def cart_count_processor(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            else:
                cart = None
        
        if cart:
            # Puedes usar .items.count() para tipos de productos 
            # o sum(item.quantity...) para el total de piezas
            count = sum(item.quantity for item in cart.items.all())
    except Exception:
        count = 0
        
    return {'global_cart_count': count}