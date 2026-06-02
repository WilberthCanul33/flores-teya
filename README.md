# 🌿 Flores Teya - Tienda de Verduras Orgánicas

E-commerce para la venta de verduras orgánicas con entrega a domicilio en Mérida, Yucatán.

---

# 🚀 Características

* ✅ Catálogo de productos orgánicos
* ✅ Carrito de compras
* ✅ Checkout con envío a domicilio / recogida en tienda
* ✅ Pagos con PayPal (Sandbox / Live)
* ✅ Registro y verificación de usuarios por email
* ✅ Panel de administración Django
* ✅ Dockerizado para fácil despliegue

---

# 📋 Requisitos previos

* Docker
* Docker Compose
* Cuenta de PayPal Developer (solo para pruebas de pago)

---

# 🚀 Instalación rápida con Docker

## 1️⃣ Clonar el repositorio

git clone https://github.com/WilberthCanul33/flores-teya.git
cd flores-teya


---

## 2️⃣ Configurar variables de entorno

Copiar el archivo de ejemplo:

cp .env.example .env

Luego editar el archivo `.env` con tus credenciales necesarias.

---

## 3️⃣ Construir y levantar los contenedores

docker-compose up -d --build

---

## 4️⃣ Ejecutar migraciones de la base de datos

docker-compose exec web python manage.py migrate

---

## 5️⃣ Cargar productos iniciales (opcional)

docker-compose exec web python scripts/load_products.py

---

## 6️⃣ Crear un superusuario para acceder al panel de administración

docker-compose exec web python manage.py createsuperuser

---

# 🌐 Acceso al sistema

Una vez ejecutado el proyecto:

Tienda:
http://localhost:8000

Panel de administración:
http://localhost:8000/admin

---

# ⚙️ Variables de entorno

El proyecto utiliza un archivo `.env` para las configuraciones sensibles.

Puedes ver un ejemplo en:

.env.example

Este archivo incluye variables como:

* SECRET_KEY
* DEBUG
* Configuración de PostgreSQL
* Credenciales de PayPal

---

# 📦 Tecnologías utilizadas

* Django
* PostgreSQL
* Docker
* HTML / CSS / JavaScript
* PayPal API


## ⚠️ Configuraciones necesarias para Producción

Al desplegar este proyecto en un servidor real, se deben realizar las siguientes configuraciones en el archivo `.env` del servidor:

### 📧 Correo Electrónico (para que lleguen los emails de verificación)

```env
# Cambiar de True a False
USE_MAILTRAP=False

# Agregar credenciales de Gmail real
EMAIL_HOST_USER=tu-email-real@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
SITE_URL=https://tu-dominio.com


# Cambiar de sandbox a live
PAYPAL_MODE=live

# Usar credenciales LIVE (no las de sandbox)
PAYPAL_CLIENT_ID=ID_LIVE_DE_PAYPAL
PAYPAL_CLIENT_SECRET=SECRET_LIVE_DE_PAYPAL
PAYPAL_RETURN_URL=https://tu-dominio.com/orders/payment-done/
PAYPAL_CANCEL_URL=https://tu-dominio.com/orders/payment-cancelled/


# Cambiar en producción
DEBUG=False
ALLOWED_HOSTS=['tu-dominio.com']
