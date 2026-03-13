/**
 * Order Detail JavaScript
 * Maneja la interactividad de la página de detalle del pedido
 */

document.addEventListener('DOMContentLoaded', function() {
    initOrderDetail();
});

function initOrderDetail() {
    // Inicializar tooltips si existen
    initTooltips();
    
    // Inicializar efectos hover en productos
    initProductHover();
    
    // Inicializar manejo de errores de imágenes
    initImageErrorHandling();
    
    // Inicializar contador para PayPal (si existe)
    initPaypalTimer();
    
    // Inicializar animación del timeline
    initTimelineAnimation();
}

/**
 * Inicializa tooltips para información adicional
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const element = e.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = tooltipText;
    tooltip.style.position = 'absolute';
    tooltip.style.backgroundColor = '#333';
    tooltip.style.color = 'white';
    tooltip.style.padding = '0.5rem 1rem';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '0.85rem';
    tooltip.style.zIndex = '1000';
    tooltip.style.pointerEvents = 'none';
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + window.scrollY + 'px';
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    
    element._tooltip = tooltip;
}

function hideTooltip(e) {
    if (e.target._tooltip) {
        e.target._tooltip.remove();
        e.target._tooltip = null;
    }
}

/**
 * Inicializa efectos hover en los productos
 */
function initProductHover() {
    const productItems = document.querySelectorAll('.product-item');
    
    productItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'var(--bg-light)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

/**
 * Maneja errores de carga de imágenes
 */
function initImageErrorHandling() {
    const productImages = document.querySelectorAll('.product-image img');
    
    productImages.forEach(img => {
        img.addEventListener('error', function() {
            // Reemplazar con icono por defecto
            const parent = this.parentElement;
            const icon = document.createElement('i');
            icon.className = 'fas fa-carrot';
            parent.innerHTML = '';
            parent.appendChild(icon);
        });
    });
}

/**
 * Inicializa temporizador para PayPal (redirección automática)
 */
function initPaypalTimer() {
    const paypalButton = document.querySelector('.paypal-button');
    
    if (paypalButton) {
        // Mostrar mensaje de redirección después de 30 segundos de inactividad
        let timeoutId = setTimeout(() => {
            showPaypalReminder();
        }, 30000);
        
        paypalButton.addEventListener('click', () => {
            clearTimeout(timeoutId);
        });
    }
}

function showPaypalReminder() {
    const paypalCard = document.querySelector('.paypal-card');
    
    if (paypalCard) {
        const reminder = document.createElement('div');
        reminder.className = 'paypal-reminder';
        reminder.style.backgroundColor = '#f8f9fa';
        reminder.style.padding = '0.5rem';
        reminder.style.marginTop = '0.5rem';
        reminder.style.borderRadius = '4px';
        reminder.style.fontSize = '0.85rem';
        reminder.style.color = '#666';
        reminder.innerHTML = '💡 Recuerda completar tu pago para procesar el pedido';
        
        paypalCard.appendChild(reminder);
    }
}

/**
 * Anima la línea de tiempo del historial
 */
function initTimelineAnimation() {
    const timelineItems = document.querySelectorAll('.history-item');
    
    // Usar Intersection Observer para animar cuando sean visibles
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.5,
            rootMargin: '0px'
        });
        
        timelineItems.forEach(item => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            item.style.transition = 'all 0.5s ease';
            observer.observe(item);
        });
    } else {
        // Fallback para navegadores antiguos
        timelineItems.forEach(item => {
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        });
    }
}

/**
 * Función para copiar número de pedido al portapapeles
 */
function copyOrderNumber() {
    const orderNumberElement = document.querySelector('.order-header h1');
    
    if (orderNumberElement) {
        const orderNumber = orderNumberElement.textContent.replace('Pedido #', '').trim();
        
        navigator.clipboard.writeText(orderNumber).then(() => {
            showNotification('Número de pedido copiado', 'success');
        }).catch(() => {
            showNotification('No se pudo copiar', 'error');
        });
    }
}

/**
 * Muestra una notificación temporal
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `order-notification ${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '1rem 2rem';
    notification.style.borderRadius = '8px';
    notification.style.color = 'white';
    notification.style.zIndex = '9999';
    notification.style.animation = 'slideIn 0.3s ease';
    
    // Colores según tipo
    if (type === 'success') {
        notification.style.backgroundColor = '#28a745';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#dc3545';
    } else {
        notification.style.backgroundColor = '#17a2b8';
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Exponer funciones globales si es necesario
window.copyOrderNumber = copyOrderNumber;
window.showNotification = showNotification;