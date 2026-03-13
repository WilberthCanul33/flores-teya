from django.shortcuts import render
from django.db.models import Q
from .models import Product, Category

def catalog_view(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Filtros
    category_filter = request.GET.get('category')
    presentation_filter = request.GET.get('presentation')
    search_query = request.GET.get('search')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    sort_by = request.GET.get('sort', 'name')
    
    # Aplicar filtros
    if category_filter and category_filter != 'all':
        products = products.filter(category__slug=category_filter)
    
    if presentation_filter and presentation_filter != 'all':
        products = products.filter(presentation=presentation_filter)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(properties__icontains=search_query)
        )
    
    if price_min:
        products = products.filter(price__gte=price_min)
    
    if price_max:
        products = products.filter(price__lte=price_max)
    
    # Ordenamiento
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    
    context = {
        'products': products,
        'categories': categories,
        'total_products': products.count(),
        'current_filters': request.GET.dict(),
    }
    
    return render(request, 'catalog/catalog.html', context)