// base.js - Script principal mejorado

// Hacer que la función sea global
window.updateCartCount = function() {
    console.log('🔄 Actualizando contador del carrito...');
    
    fetch('/cart/count/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache'
        },
        cache: 'no-store'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const cartBadges = document.querySelectorAll('#cartCount, .cart-badge');
        cartBadges.forEach(badge => {
            if (badge.textContent !== String(data.count)) {
                badge.textContent = data.count;
                if (data.count > 0) {
                    badge.style.animation = 'pulse 0.5s ease';
                    setTimeout(() => {
                        badge.style.animation = '';
                    }, 500);
                }
            }
        });
    })
    .catch(error => {
        console.error('❌ Error actualizando contador:', error);
    });
};

// Añadir animación pulse
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.3); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);

// Mobile menu mejorado
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ base.js cargado');
    
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            mobileMenu.classList.toggle('active');
            
            // Cambiar ícono
            const icon = this.querySelector('i');
            if (mobileMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
        
        // Cerrar menú al hacer click fuera
        document.addEventListener('click', function(event) {
            if (!mobileMenu.contains(event.target) && 
                !mobileMenuBtn.contains(event.target) && 
                mobileMenu.classList.contains('active')) {
                mobileMenu.classList.remove('active');
                const icon = mobileMenuBtn.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
        
        // Prevenir que clicks dentro del menú lo cierren
        mobileMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideIn 0.3s reverse';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Actualizar contador del carrito al cargar
    setTimeout(() => {
        window.updateCartCount();
    }, 100);
});

// Función para obtener CSRF token
window.getCookie = function(name) {
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
};

// Actualizar cuando el usuario vuelve a la página
window.addEventListener('pageshow', function() {
    window.updateCartCount();
});

// Actualizar periódicamente
setInterval(() => {
    window.updateCartCount();
}, 30000);


// Cerrar el menú al hacer clic fuera
document.addEventListener('click', function(event) {
    const menu = document.getElementById('languageMenu');
    const button = document.querySelector('.language-btn');
    
    if (button && !button.contains(event.target) && menu && !menu.contains(event.target)) {
        menu.classList.remove('show');
    }
});
