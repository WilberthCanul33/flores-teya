// profile-edit.js
document.addEventListener('DOMContentLoaded', function() {
    // Auto-formatear teléfono
    const phoneInput = document.querySelector('input[name="phone"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value.length <= 3) {
                    value = value;
                } else if (value.length <= 6) {
                    value = value.slice(0, 3) + '-' + value.slice(3);
                } else {
                    value = value.slice(0, 3) + '-' + value.slice(3, 6) + '-' + value.slice(6, 10);
                }
                e.target.value = value;
            }
        });
    }

    // Validar código postal en tiempo real
    const cpInput = document.querySelector('input[name="postal_code"]');
    if (cpInput) {
        cpInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 5) {
                value = value.slice(0, 5);
            }
            e.target.value = value;
            
            // Validar formato
            if (value.length === 5) {
                // Aquí podrías hacer una llamada AJAX a SEPOMEX
                validatePostalCode(value);
            }
        });
    }

    // Auto-mayúsculas en campos de texto
    const textInputs = document.querySelectorAll('input[type="text"]:not([name="phone"]):not([name="postal_code"])');
    textInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            // Capitalizar primera letra de cada palabra
            let value = e.target.value.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
            e.target.value = value;
        });
    });

    // Confirmar antes de salir si hay cambios
    let formChanged = false;
    const form = document.getElementById('profileEditForm');
    const formInputs = form.querySelectorAll('input, select, textarea');
    
    formInputs.forEach(input => {
        input.addEventListener('change', () => {
            formChanged = true;
        });
    });
    
    window.addEventListener('beforeunload', (e) => {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
    
    form.addEventListener('submit', () => {
        formChanged = false;
    });
});

// Función para buscar dirección por código postal
function searchPostalCode() {
    const cpInput = document.querySelector('input[name="postal_code"]');
    const cp = cpInput.value.replace(/\D/g, '');
    
    if (cp.length !== 5) {
        alert('Ingresa un código postal válido de 5 dígitos');
        return;
    }
    
    // Aquí puedes implementar la llamada a la API de SEPOMEX
    // Por ahora mostraremos un mensaje simulado
    alert(`Buscando dirección para CP ${cp}...\n(Integra aquí la API de SEPOMEX para autocompletar)`);
    
    // Ejemplo de cómo sería con fetch (cuando tengas la API)
    /*
    fetch(`https://api.sepomex.com.mx/cp/${cp}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector('input[name="city"]').value = data.city;
                document.querySelector('select[name="state"]').value = data.state;
                // Autocompletar otros campos
            } else {
                alert('No se encontró la dirección para este código postal');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al buscar la dirección');
        });
    */
}

// Validación en tiempo real
function validatePostalCode(cp) {
    // Aquí puedes implementar validación básica
    const cpRegex = /^\d{5}$/;
    if (cpRegex.test(cp)) {
        console.log('CP válido:', cp);
        // Cambiar color del borde
        document.querySelector('input[name="postal_code"]').style.borderColor = '#28a745';
    } else {
        document.querySelector('input[name="postal_code"]').style.borderColor = '#dc3545';
    }
}

// Guardar cambios con animación
function saveWithAnimation(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    button.disabled = true;
    
    // La animación se revertirá cuando el formulario se envíe
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}