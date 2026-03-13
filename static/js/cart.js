// cart.js - Funcionalidades del carrito

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ cart.js cargado');
    
    // Inicializar tooltips
    initTooltips();
    
    // Manejar cambios en inputs de cantidad
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.dataset.productId;
            updateQuantityInput(productId, this.value);
        });
    });
});

// Función para agregar al carrito
function addToCart(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            // Usar la función GLOBAL
            if (typeof window.updateCartCount === 'function') {
                window.updateCartCount();
            }
            
            // Animar el botón
            const button = event.currentTarget;
            button.classList.add('added');
            setTimeout(() => button.classList.remove('added'), 1000);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Función para actualizar cantidad
function updateQuantity(productId, change) {
    const item = document.querySelector(`[data-product-id="${productId}"]`);
    const input = item.querySelector('.quantity-input');
    let newQuantity = parseInt(input.value) + change;
    
    if (newQuantity < 1) {
        removeFromCart(productId);
        return;
    }
    
    const maxStock = parseInt(input.max);
    if (newQuantity > maxStock) {
        showNotification(`Stock máximo disponible: ${maxStock}`, 'warning');
        return;
    }
    
    updateQuantityInput(productId, newQuantity);
}

// Función para actualizar input de cantidad
function updateQuantityInput(productId, quantity) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    
    fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartTotals(data);
            showNotification('Carrito actualizado', 'success');
        }
    })
    .catch(error => console.error('Error:', error));
}

// Función para eliminar del carrito
function removeFromCart(productId) {
    const formData = new FormData();
    
    fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const item = document.querySelector(`[data-product-id="${productId}"]`);
            item.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                item.remove();
                updateCartTotals(data);
                checkEmptyCart();
            }, 300);
            showNotification('Producto eliminado', 'success');
        }
    })
    .catch(error => console.error('Error:', error));
}

// Función para actualizar totales del carrito
function updateCartTotals(data) {
    // Usar la función GLOBAL
    if (typeof window.updateCartCount === 'function') {
        window.updateCartCount();
    }
    
    // Actualizar subtotal si existe
    const subtotalElement = document.querySelector('.summary-row:first-child span:last-child');
    if (subtotalElement && data.cart_total) {
        subtotalElement.textContent = `$${data.cart_total.toFixed(2)}`;
    }
    
    // Recargar la página para actualizar todos los cálculos
    setTimeout(() => location.reload(), 500);
}

// Función para aplicar cupón
function applyCoupon() {
    const couponInput = document.getElementById('couponCode');
    const coupon = couponInput.value.trim();
    
    if (!coupon) {
        showNotification('Ingresa un código de cupón', 'warning');
        return;
    }
    
    showNotification('Cupón aplicado: 10% de descuento', 'success');
    couponInput.value = '';
}

// Función para agregar rápido desde recomendados
function addToCartQuick(productId) {
    addToCart(productId, 1);
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                       type === 'warning' ? 'fa-exclamation-triangle' : 
                       'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Función para verificar si el carrito está vacío
function checkEmptyCart() {
    const cartItems = document.querySelectorAll('.cart-item');
    if (cartItems.length === 0) {
        location.reload();
    }
}

// Función para inicializar tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

// Funciones para tooltips
function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.dataset.tooltip;
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    tooltip.style.left = rect.left + (rect.width - tooltip.offsetWidth) / 2 + 'px';
    tooltip.classList.add('show');
}

function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(t => t.remove());
}

// Función para obtener CSRF token (usa la global si existe)
function getCookie(name) {
    if (typeof window.getCookie === 'function') {
        return window.getCookie(name);
    }
    
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

// Estilos para notificaciones y tooltips
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        gap: 1rem;
        transform: translateX(120%);
        transition: transform 0.3s ease;
        z-index: 3000;
        border-left: 4px solid;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left-color: #28a745;
    }
    
    .notification-success i {
        color: #28a745;
    }
    
    .notification-warning {
        border-left-color: #ffc107;
    }
    
    .notification-warning i {
        color: #ffc107;
    }
    
    .notification-error {
        border-left-color: #dc3545;
    }
    
    .notification-error i {
        color: #dc3545;
    }
    
    .notification-info {
        border-left-color: var(--primary-color);
    }
    
    .notification-info i {
        color: var(--primary-color);
    }
    
    .tooltip {
        position: fixed;
        background: var(--text-dark);
        color: white;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
        z-index: 4000;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .tooltip.show {
        opacity: 1;
    }
    
    .tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border-width: 5px;
        border-style: solid;
        border-color: var(--text-dark) transparent transparent transparent;
    }
    
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(-100%);
        }
    }
    
    .btn-add-to-cart.added {
        background: #28a745;
        transform: scale(1.1);
    }
`;
document.head.appendChild(style);