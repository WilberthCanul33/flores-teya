from datetime import datetime, timedelta
from django.utils import timezone

def calculate_delivery_date(order_datetime=None):
    """
    Calcula la fecha de entrega según las reglas de negocio:
    - Si se pide MARTES antes de las 12:00 PM → se entrega el MISMO MARTES
    - Si se pide VIERNES antes de las 12:00 PM → se entrega el MISMO VIERNES
    - Cualquier otro día o después del mediodía → se entrega el siguiente día de envío
    """
    if order_datetime is None:
        order_datetime = timezone.now()
    
    # Obtener día de la semana (0=lunes, 1=martes, 2=miércoles, 3=jueves, 4=viernes, 5=sábado, 6=domingo)
    day_of_week = order_datetime.weekday()
    hour = order_datetime.hour
    minute = order_datetime.minute
    
    # Crear objeto datetime para hoy (solo fecha)
    today = order_datetime.date()
    
    print(f"📅 Día de la semana: {day_of_week} (0=lun, 1=martes, 4=viernes)")
    print(f"⏰ Hora: {hour}:{minute}")
    
    # Reglas de programación de envío
    if day_of_week == 1:  # MARTES (1)
        if hour < 12:  # Antes de las 12:00 PM
            print("✅ Entrega el MISMO MARTES (antes del mediodía)")
            delivery_date = today
        else:
            print("📅 Entrega el VIERNES (después del mediodía del martes)")
            # Calcular días hasta viernes (4)
            days_until_friday = 4 - day_of_week
            delivery_date = today + timedelta(days=days_until_friday)
    
    elif day_of_week == 4:  # VIERNES (4)
        if hour < 12:  # Antes de las 12:00 PM
            print("✅ Entrega el MISMO VIERNES (antes del mediodía)")
            delivery_date = today
        else:
            print("📅 Entrega el MARTES PRÓXIMO (después del mediodía del viernes)")
            # Calcular días hasta martes (1)
            days_until_tuesday = (1 - day_of_week) % 7
            delivery_date = today + timedelta(days=days_until_tuesday)
    
    elif day_of_week == 0:  # LUNES
        print("📅 Entrega el MARTES (pedido en lunes)")
        delivery_date = today + timedelta(days=1)
    
    elif day_of_week == 2:  # MIÉRCOLES
        print("📅 Entrega el VIERNES (pedido en miércoles)")
        days_until_friday = 4 - day_of_week
        delivery_date = today + timedelta(days=days_until_friday)
    
    elif day_of_week == 3:  # JUEVES
        print("📅 Entrega el VIERNES (pedido en jueves)")
        days_until_friday = 4 - day_of_week
        delivery_date = today + timedelta(days=days_until_friday)
    
    elif day_of_week == 5:  # SÁBADO
        print("📅 Entrega el MARTES (pedido en sábado)")
        days_until_tuesday = (1 - day_of_week) % 7
        delivery_date = today + timedelta(days=days_until_tuesday)
    
    else:  # DOMINGO (6)
        print("📅 Entrega el MARTES (pedido en domingo)")
        days_until_tuesday = (1 - day_of_week) % 7
        delivery_date = today + timedelta(days=days_until_tuesday)
    
    return delivery_date