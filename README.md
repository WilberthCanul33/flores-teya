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

**IMPORTANTE:** Para que los correos de verificación lleguen a los usuarios reales, debes usar una cuenta de Gmail y generar una **Contraseña de Aplicación** (requiere tener verificación en dos pasos activada).

Cambia la configuración de correo de pruebas (Mailtrap) a un servidor SMTP real como Gmail.

```env
# Cambiar de True a False
USE_MAILTRAP=False

# Agregar credenciales de Gmail real
EMAIL_HOST_USER=tu-email-real@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
SITE_URL=https://tu-dominio.com
```

### 💰 PayPal (para pagos reales)

**IMPORTANTE:** Por defecto, PayPal está en modo **Sandbox** (pruebas, dinero ficticio). Para recibir pagos reales, debes cambiarlo a **Live**.

## 🔐 Configuración de PayPal

Para que los pagos funcionen, necesitas obtener tus credenciales de PayPal:

### Para pruebas (Sandbox) - Dinero ficticio

1. Ve a [https://developer.paypal.com/dashboard/](https://developer.paypal.com/dashboard/)
2. Inicia sesión con tu cuenta de PayPal
3. Asegúrate de estar en modo **Sandbox** (toggle en la parte superior)
4. Ve a **"My Apps & Credentials"**
5. Crea una aplicación o usa la que tengas
6. Copia el **Client ID** y **Client Secret** de Sandbox

### Para producción (Live) - Dinero real

1. Cambia el toggle de **Sandbox** a **Live**
2. Crea una aplicación o usa la que tengas
3. Copia el **Client ID** y **Client Secret** de Live
4. En tu archivo `.env`, cambia `PAYPAL_MODE=sandbox` a `PAYPAL_MODE=live`
5. Actualiza las URLs de retorno con tu dominio real:

```env
PAYPAL_RETURN_URL=https://tudominio.com/orders/payment-done/
PAYPAL_CANCEL_URL=https://tudominio.com/orders/payment-cancelled/

Si ya has probado los pagos en modo Sandbox (pruebas), cámbialo a **Live** para que los pagos sean reales.

```env
# Cambiar de sandbox a live
PAYPAL_MODE=live

# Usar credenciales LIVE (no las de sandbox)
PAYPAL_CLIENT_ID=ID_LIVE_DE_PAYPAL
PAYPAL_CLIENT_SECRET=SECRET_LIVE_DE_PAYPAL
PAYPAL_RETURN_URL=https://tu-dominio.com/orders/payment-done/
PAYPAL_CANCEL_URL=https://tu-dominio.com/orders/payment-cancelled/
```

### 🔒 Seguridad

Para el entorno de producción, es vital cambiar estas configuraciones:

```env
# Cambiar en producción
DEBUG=False
ALLOWED_HOSTS=['tu-dominio.com']
```