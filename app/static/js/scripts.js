// scripts.js - Funciones JavaScript para ArteVivo

// Configuración global para incluir el token CSRF en todas las solicitudes AJAX
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Configurar jQuery AJAX (si se usa jQuery)
if (typeof $ !== 'undefined') {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
            }
        }
    });
}

// Configurar fetch API para incluir CSRF token
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    options = options || {};
    if (!options.headers) {
        options.headers = {};
    }
    
    if (options.method && options.method !== 'GET' && options.method !== 'HEAD') {
        options.headers['X-CSRFToken'] = getCsrfToken();
    }
    
    return originalFetch(url, options);
};

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
    
    // Inicializar popovers de Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    })
    
    // Auto-cerrar alertas después de 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Validación de formularios
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Función para confirmar acciones
function confirmarAccion(mensaje) {
    return confirm(mensaje || '¿Estás seguro de realizar esta acción?');
}

// Función para formatear precios
function formatearPrecio(precio) {
    return '$' + parseFloat(precio).toFixed(2);
}

// Función para manejar la selección de asientos
function seleccionarAsiento(asientoId, fila, numero, precio, estado) {
    // Esta función se puede implementar según sea necesario
    console.log('Asiento seleccionado:', asientoId, fila, numero, precio, estado);
}
