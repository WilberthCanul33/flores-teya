// catalog.js - Funcionalidades específicas del catálogo

/**
 * Función auxiliar para obtener el CSRF Token (Indispensable para POST)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Agrega un producto al carrito mediante AJAX
 */
function addToCart(productId, event) {
    if (event) event.preventDefault();
    
    console.log('🔵 Iniciando proceso para producto ID:', productId);
    
    // 1. Localizar el botón
    const button = event ? event.currentTarget : document.querySelector(`button[onclick*="${productId}"]`);
    
    if (!button) {
        console.error('❌ No se encontró el botón en el DOM');
        return;
    }
    
    const originalText = button.innerHTML;
    const originalBg = button.style.backgroundColor;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agregando...';
    button.disabled = true;
    
    const csrftoken = getCookie('csrftoken');
    const formData = new FormData();
    formData.append('quantity', 1);
    formData.append('csrfmiddlewaretoken', csrftoken);
    
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) return response.json().then(err => { throw err; });
        return response.json();
    })
    .then(data => {
        if (data.success) {
            button.innerHTML = '<i class="fas fa-check"></i> Agregado';
            button.style.backgroundColor = '#28a745';
            button.style.color = 'white';
            
            // Actualizar contador global
            const cartBadges = document.querySelectorAll('#cartCount, .cart-badge');
            cartBadges.forEach(badge => {
                badge.textContent = data.cart_count;
                badge.style.transform = 'scale(1.3)';
                setTimeout(() => badge.style.transform = 'scale(1)', 200);
            });
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.backgroundColor = originalBg;
                button.disabled = false;
            }, 1500);
        }
    })
    .catch(error => {
        console.error('❌ Error en addToCart:', error);
        alert('Error: ' + (error.message || 'No se pudo agregar'));
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

/**
 * Función para vista rápida - MODAL CON DESCRIPCIÓN COMPLETA
 */
function quickView(productId, event) {
    if (event) event.preventDefault();
    console.log('🔍 Vista rápida para producto ID:', productId);
    
    // Buscar la tarjeta del producto
    const productCard = document.querySelector(`.product-card[data-product-id="${productId}"]`);
    
    if (!productCard) {
        console.error('❌ No se encontró la tarjeta del producto');
        return;
    }
    
    // Extraer información del producto
    const productName = productCard.querySelector('.product-name').textContent;
    const productPrice = productCard.querySelector('.current-price').textContent;
    const productPresentation = productCard.querySelector('.presentation').textContent;
    const productProperties = productCard.querySelector('.product-properties').textContent;
    const productImage = productCard.querySelector('.product-image img')?.src || null;
    
    // Obtener el modal y su contenido
    const modal = document.getElementById('quickViewModal');
    const modalContent = document.getElementById('quickViewContent');
    
    // Construir el HTML del modal
    modalContent.innerHTML = `
        <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px;">
                ${productImage 
                    ? `<img src="${productImage}" alt="${productName}" style="width: 100%; border-radius: 10px; box-shadow: var(--shadow-md);">` 
                    : `<div style="width: 100%; height: 250px; background: var(--light-green); border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-image" style="font-size: 5rem; color: var(--text-light);"></i>
                       </div>`
                }
            </div>
            <div style="flex: 2;">
                <h2 style="font-size: 2rem; color: var(--primary-green); margin-bottom: 0.5rem;">${productName}</h2>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; font-weight: 700; color: var(--primary-green);">${productPrice}</span>
                    <span style="font-size: 1.2rem; color: var(--text-light);">${productPresentation}</span>
                </div>
                
                <h3 style="font-size: 1.2rem; color: var(--text-dark); margin-bottom: 0.5rem;">
                    <i class="fas fa-leaf" style="color: var(--primary-green);"></i> Propiedades:
                </h3>
                <p style="font-size: 1rem; color: var(--text-light); line-height: 1.6; margin-bottom: 2rem;">
                    ${productProperties}
                </p>
                
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <button onclick="addToCart(${productId}, event)" class="btn-add-to-cart" style="flex: 1; padding: 1rem;">
                        <i class="fas fa-shopping-cart"></i> Agregar al carrito
                    </button>
                    <button onclick="closeQuickView()" class="btn-quick-view" style="flex: 0; padding: 1rem 2rem;">
                        <i class="fas fa-times"></i> Cerrar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Mostrar el modal
    modal.style.display = 'block';
    
    // Evitar scroll en el body
    document.body.style.overflow = 'hidden';
}

/**
 * Cerrar el modal de vista rápida
 */
function closeQuickView() {
    const modal = document.getElementById('quickViewModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

/**
 * Filtros
 */
function applyFilters() {
    const searchInput = document.getElementById('searchInput');
    const search = searchInput ? searchInput.value : '';
    const category = document.getElementById('categoryFilter').value;
    const presentation = document.getElementById('presentationFilter').value;
    const sort = document.getElementById('sortFilter').value;
    const priceMin = document.getElementById('priceMin').value;
    const priceMax = document.getElementById('priceMax').value;
    
    let url = new URL(window.location.href);
    if (search) url.searchParams.set('search', search); else url.searchParams.delete('search');
    if (category && category !== 'all') url.searchParams.set('category', category); else url.searchParams.delete('category');
    if (presentation && presentation !== 'all') url.searchParams.set('presentation', presentation); else url.searchParams.delete('presentation');
    if (sort) url.searchParams.set('sort', sort); else url.searchParams.delete('sort');
    if (priceMin) url.searchParams.set('price_min', priceMin); else url.searchParams.delete('price_min');
    if (priceMax) url.searchParams.set('price_max', priceMax); else url.searchParams.delete('price_max');
    
    url.searchParams.delete('page');
    window.location.href = url.toString();
}

function clearFilters() {
    window.location.href = window.location.pathname;
}

// Inicializar eventos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ catalog.js cargado');
    
    // Cerrar modal con la tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeQuickView();
        }
    });
    
    // Cerrar modal al hacer clic fuera del contenido
    const modal = document.getElementById('quickViewModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeQuickView();
            }
        });
    }
});