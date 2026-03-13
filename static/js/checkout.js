/**
 * Checkout JavaScript
 * Maneja toda la lógica del proceso de checkout
 */

const CheckoutApp = {
    // Variables de instancia
    homeDeliveryCost: 0,
    subtotal: 0,

    /**
     * Inicializa la aplicación
     */
    init(config) {
        this.homeDeliveryCost = config.homeDeliveryCost || 0;
        this.subtotal = config.subtotal || 0;

        this.initEventListeners();
        this.initExistingSelection();
        this.initDateSelector();
    },

    /**
     * Inicializa los event listeners
     */
    initEventListeners() {
        // Validación en tiempo real para campos de dirección
        ['colonia', 'calle', 'phone'].forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', () => this.clearFieldError(fieldId));
                field.addEventListener('blur', (e) => this.validateField(fieldId, e.target));
            }
        });

        // Validación del formulario
        const form = document.getElementById('checkoutForm');
        if (form) {
            form.addEventListener('submit', (e) => this.validateForm(e));
        }
    },

    /**
     * Inicializa selector de fechas
     */
    initDateSelector() {
        this.generateAvailableDates();
    },

    generateAvailableDates() {
        const select = document.getElementById('pickupDate');
        if (!select) return;

        // Limpiar opciones existentes
        select.innerHTML = '<option value="">-- Elige un día --</option>';

        const now = new Date();
        const currentHour = now.getHours();
        const currentMinutes = now.getMinutes();
        const currentDay = now.getDay(); // 0=domingo, 1=lunes, ..., 6=sábado

        const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

        console.log(`🕒 Hora actual: ${currentHour}:${currentMinutes}`);
        console.log(`📅 Día actual: ${currentDay}`);

        // Generar fechas para los próximos 30 días
        for (let i = 0; i < 30; i++) {
            const date = new Date();
            date.setDate(now.getDate() + i);
            date.setHours(0, 0, 0, 0); // Resetear hora para comparación

            const dayOfWeek = date.getDay(); // 0=domingo, 1=lunes, ..., 6=sábado

            // Solo mostrar lunes a sábado (1-6)
            if (dayOfWeek >= 1 && dayOfWeek <= 6) {

                // Verificar si es el día de HOY
                const isToday = (i === 0);

                // Si es hoy, verificar si aún estamos dentro del horario (antes de las 5 PM)
                if (isToday) {
                    // Si ya pasaron las 5 PM (17:00), NO mostrar hoy como opción
                    if (currentHour >= 17) {
                        console.log(`❌ Hoy después de 5 PM - no disponible`);
                        continue; // Saltar este día (hoy no disponible)
                    }

                    // Si es sábado después de la 1 PM (opcional, para el punto 1)
                    if (dayOfWeek === 6 && currentHour >= 13) {
                        console.log(`❌ Sábado después de 1 PM - no disponible`);
                        continue;
                    }
                }

                const dayName = date.toLocaleDateString('es-MX', { weekday: 'long' });
                const day = date.getDate();
                const month = monthNames[date.getMonth()];
                const year = date.getFullYear();

                // Formato para mostrar
                let displayDate = `${dayName.charAt(0).toUpperCase() + dayName.slice(1)} ${day} de ${month} ${year}`;

                // Si es hoy y estamos dentro del horario, agregar indicador
                if (isToday) {
                    displayDate += ` (HOY - disponible hasta 5:00 PM)`;
                }

                // Formato para el value: YYYY-MM-DD
                const valueDate = date.toISOString().split('T')[0];

                const option = document.createElement('option');
                option.value = valueDate;
                option.textContent = displayDate;

                // Marcar como seleccionado por defecto el primer día disponible
                if (select.options.length === 1) { // Solo la opción vacía existe
                    option.selected = true;
                }

                select.appendChild(option);
            }
        }

        // Si no hay opciones disponibles, mostrar mensaje
        if (select.options.length <= 1) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No hay días disponibles en este momento';
            option.disabled = true;
            select.appendChild(option);
        }
    },
    /**
     * Selecciona método de entrega
     */
    selectDeliveryMethod(method, event) {
        // Remover clase selected de todas las opciones
        document.querySelectorAll('.delivery-option').forEach(opt => {
            opt.classList.remove('selected');
        });

        event.currentTarget.classList.add('selected');

        if (method === 'pickup') {
            this.selectPickupMethod();
        } else {
            this.selectHomeDeliveryMethod();
        }

        this.clearAllErrors();
    },

    /**
     * Maneja selección de método pickup
     */
    selectPickupMethod() {
        document.getElementById('method_pickup').checked = true;
        document.getElementById('pickupPoints').style.display = 'block';
        document.getElementById('homeDeliveryInfo').style.display = 'none';

        // Ocultar selector de fecha
        const dateSelector = document.getElementById('pickupDateSelector');
        if (dateSelector) {
            dateSelector.style.display = 'none';
        }

        // Actualizar resumen
        document.getElementById('shippingAmount').textContent = '$0.00';
        this.updateTotal(0);

        // Remover required de campos de dirección
        this.removeRequiredFromAddressFields();
    },

    /**
     * Maneja selección de método home delivery
     */
    selectHomeDeliveryMethod() {
        document.getElementById('method_home').checked = true;
        document.getElementById('pickupPoints').style.display = 'none';
        document.getElementById('homeDeliveryInfo').style.display = 'block';

        // Ocultar selector de fecha
        const dateSelector = document.getElementById('pickupDateSelector');
        if (dateSelector) {
            dateSelector.style.display = 'none';
        }

        // Actualizar resumen
        document.getElementById('shippingAmount').textContent = '$50.00';
        this.updateTotal(50);

        // Agregar required a campos de dirección
        this.addRequiredToAddressFields();
    },

    /**
     * Selecciona punto de recogida
     */
    selectPickupPoint(point, event) {
        event.stopPropagation();

        // Seleccionar radio button correspondiente
        if (point === 'mercado') {
            document.getElementById('point_mercado').checked = true;
            this.handleMercadoSelection();
        } else {
            document.getElementById('point_segundo').checked = true;
            this.handleSegundoLugarSelection();
        }

        // Actualizar UI de tarjetas
        this.updatePickupCardsSelection(event.currentTarget);
    },

    /**
     * Maneja selección del punto Mercado
     */
    handleMercadoSelection() {
        const dateSelector = document.getElementById('pickupDateSelector');
        if (dateSelector) {
            dateSelector.style.display = 'none';
        }

        const pickupDate = document.getElementById('pickupDate');
        if (pickupDate) {
            pickupDate.required = false;
        }
    },

    /**
     * Maneja selección del punto Segundo Lugar
     */
    handleSegundoLugarSelection() {
        const dateSelector = document.getElementById('pickupDateSelector');
        if (dateSelector) {
            dateSelector.style.display = 'block';
        }

        const pickupDate = document.getElementById('pickupDate');
        if (pickupDate) {
            pickupDate.required = true;
        }
    },

    /**
     * Actualiza la selección visual de las tarjetas de pickup
     */
    updatePickupCardsSelection(selectedCard) {
        document.querySelectorAll('.pickup-card').forEach(card => {
            card.classList.remove('selected');
        });
        selectedCard.classList.add('selected');
    },

    /**
     * Actualiza el total en el resumen
     */
    updateTotal(shippingCost) {
        const newTotal = this.subtotal + shippingCost;
        document.getElementById('totalAmount').textContent = '$' + newTotal.toFixed(2);
    },

    /**
     * Agrega required a campos de dirección
     */
    addRequiredToAddressFields() {
        ['colonia', 'calle', 'phone'].forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.required = true;
                element.setAttribute('required', 'required');
            }
        });
    },

    /**
     * Remueve required de campos de dirección
     */
    removeRequiredFromAddressFields() {
        ['colonia', 'calle', 'phone'].forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.required = false;
                element.removeAttribute('required');
            }
        });
    },

    /**
     * Limpia todos los errores
     */
    clearAllErrors() {
        document.querySelectorAll('input.error, textarea.error').forEach(el => {
            el.classList.remove('error');
        });

        document.querySelectorAll('.error-message').forEach(el => {
            el.classList.remove('show');
        });
    },

    /**
     * Limpia error de un campo específico
     */
    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        const errorElement = document.getElementById(fieldId + '-error');

        if (errorElement) {
            errorElement.classList.remove('show');
        }

        if (field) {
            field.classList.remove('error');
        }
    },

    /**
     * Muestra error en un campo
     */
    showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const errorElement = document.getElementById(fieldId + '-error');

        if (field) {
            field.classList.add('error');
        }

        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
    },

    /**
     * Valida un campo específico
     */
    validateField(fieldId, element) {
        if (element.required && !element.value.trim()) {
            this.showFieldError(fieldId, 'Este campo es obligatorio');
            return false;
        }

        if (fieldId === 'phone' && element.value.trim()) {
            const phoneRegex = /^[\d\s\+\-\(\)]{10,}$/;
            if (!phoneRegex.test(element.value.trim())) {
                this.showFieldError(fieldId, 'Ingresa un teléfono válido (mínimo 10 dígitos)');
                return false;
            }
        }

        return true;
    },

    /**
     * Valida campos de dirección
     */
    validateAddressFields() {
        let isValid = true;
        const fields = [
            { id: 'colonia', name: 'La colonia' },
            { id: 'calle', name: 'La calle' },
            { id: 'phone', name: 'El teléfono' }
        ];

        fields.forEach(field => {
            const element = document.getElementById(field.id);
            if (!element.value.trim()) {
                this.showFieldError(field.id, `${field.name} es obligatoria`);
                isValid = false;
            } else if (field.id === 'phone' && !/^[\d\s\+\-\(\)]{10,}$/.test(element.value.trim())) {
                this.showFieldError(field.id, 'Ingresa un teléfono válido (mínimo 10 dígitos)');
                isValid = false;
            }
        });

        return isValid;
    },

    /**
     * Valida el formulario antes de enviar
     */
    validateForm(e) {
        e.preventDefault();

        this.clearAllErrors();

        // Validar método de entrega
        const deliveryMethod = document.querySelector('input[name="delivery_method"]:checked');
        if (!deliveryMethod) {
            alert('Por favor selecciona un método de entrega');
            return;
        }

        // Validar según método seleccionado
        if (deliveryMethod.value === 'pickup') {
            if (!this.validatePickupMethod()) return;
        } else if (deliveryMethod.value === 'home_delivery') {
            if (!this.validateAddressFields()) {
                this.scrollToFirstError();
                return;
            }
        }

        // Enviar formulario
        e.target.submit();
    },

    /**
     * Valida método pickup
     */
    validatePickupMethod() {
        const pickupPoint = document.querySelector('input[name="pickup_point"]:checked');
        if (!pickupPoint) {
            alert('Por favor selecciona un punto de recogida');
            return false;
        }

        if (pickupPoint.value === 'segundo_lugar') {
            const pickupDate = document.getElementById('pickupDate').value;
            if (!pickupDate) {
                alert('Por favor selecciona un día de recogida');
                return false;
            }
        }

        return true;
    },

    /**
     * Scroll al primer error
     */
    scrollToFirstError() {
        const firstError = document.querySelector('.error-message.show');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    },

    /**
     * Inicializa selección existente (si hay datos precargados)
     */
    initExistingSelection() {
        const selectedMethod = document.querySelector('input[name="delivery_method"]:checked');
        if (selectedMethod) {
            if (selectedMethod.value === 'home_delivery') {
                this.addRequiredToAddressFields();
                document.getElementById('homeDeliveryInfo').style.display = 'block';
                document.querySelector('.delivery-option.selected')?.classList.add('selected');
            } else if (selectedMethod.value === 'pickup') {
                document.getElementById('pickupPoints').style.display = 'block';
            }
        }

        const selectedPickupPoint = document.querySelector('input[name="pickup_point"]:checked');
        if (selectedPickupPoint && selectedPickupPoint.value === 'segundo_lugar') {
            document.getElementById('pickupDateSelector').style.display = 'block';
        }
    }
};

// Exponer la aplicación globalmente
window.CheckoutApp = CheckoutApp;