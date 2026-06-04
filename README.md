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

### 🔐 SECRET_KEY (CRÍTICO para seguridad)

La `SECRET_KEY` es una clave secreta que Django utiliza para:
- Firmar cookies de sesión
- Proteger tokens CSRF
- Firmar mensajes de reseteo de contraseña

**⚠️ IMPORTANTE:**
- **NUNCA** uses la clave de ejemplo en producción
- **NUNCA** compartas tu `SECRET_KEY` públicamente
- **DEBE** ser única para cada despliegue

**Cómo generar una SECRET_KEY segura:**

```bash
# Opción 1: Usando Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Opción 2: Usando openssl (si está disponible)
openssl rand -base64 50

# Opción 3: Usando el generador online (desconectado de internet)
# https://djecrety.ir/

```

## 🔧 Modos de ejecución

### Modo desarrollo (para programar y probar localmente)

# 3. Levantar los contenedores

```bash
docker-compose up -d
```

# 4. Ejecutar migraciones

```bash
docker-compose exec web python manage.py migrate
```

# 5. Cargar productos (opcional)

```bash
docker-compose exec web python scripts/load_products.py
```

# 6. Crear superusuario

```bash
docker-compose exec web python manage.py createsuperuser
```


# 🌐 Acceso al sistema

Una vez ejecutado el proyecto:

Tienda:
http://localhost:8000/

Panel de administración:
http://localhost:8000/admin


## 🚀 Despliegue en producción (con Gunicorn + Nginx)

> ⚠️ **Solo para servidor real, NO para desarrollo local**

### Configurar `.env` con variables de producción

```env

DEBUG=False

ALLOWED_HOSTS=flores.inmerso.io,www.flores.inmerso.io

```

## Construir y levantar con Nginx

```bash
docker-compose -f docker-compose.prod.yml build
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Migrar base de datos

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

## Cargar productos iniciales (opcional)

```bash
docker-compose -f docker-compose.prod.yml exec web python scripts/load_products.py
```

## Verificar que todo funciona

```bash
docker-compose -f docker-compose.prod.yml ps
```

```bash
docker-compose -f docker-compose.prod.yml logs -f web
```

## Crear superusuario en producción

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Ver estado de los contenedores

```bash
docker-compose -f docker-compose.prod.yml ps
```

## Ver logs

```bash
docker-compose -f docker-compose.prod.yml logs -f web
```




# 🌐 Acceso al sistema

Una vez ejecutado el proyecto:

Tienda:
http://localhost

Panel de administración:
http://localhost/admin

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

# 🔴 CRÍTICO: Debe ser tu dominio real, NO localhost.
SITE_URL=https://tu-dominio.com

# En `settings.py`, `SITE_URL` se configura así:

SITE_URL = config('SITE_URL', default='http://localhost:8000')


```


### 💰 PayPal (para pagos reales)

**IMPORTANTE:** Por defecto, PayPal está en modo **Sandbox** (pruebas, dinero ficticio). Para recibir pagos reales, debes cambiarlo a **Live**.

#### 🔐 Configuración de PayPal

Para que los pagos funcionen, necesitas obtener tus credenciales de PayPal:

**Para pruebas (Sandbox) - Dinero ficticio:**

1. Ve a [https://developer.paypal.com/dashboard/](https://developer.paypal.com/dashboard/)
2. Inicia sesión con tu cuenta de PayPal
3. Asegúrate de estar en modo **Sandbox** (toggle en la parte superior)
4. Ve a **"My Apps & Credentials"**
5. Crea una aplicación o usa la que tengas
6. Copia el **Client ID** y **Client Secret** de Sandbox

**Para producción (Live) - Dinero real:**

1. Cambia el toggle de **Sandbox** a **Live**
2. Crea una aplicación o usa la que tengas
3. Copia el **Client ID** y **Client Secret** de Live
4. En tu archivo `.env`, cambia `PAYPAL_MODE=sandbox` a `PAYPAL_MODE=live`
5. Actualiza las URLs de retorno con tu dominio real:

```env
# Cambiar de sandbox a live
PAYPAL_MODE=live

# Usar credenciales LIVE (no las de sandbox)
PAYPAL_CLIENT_ID=ID_LIVE_DE_PAYPAL
PAYPAL_CLIENT_SECRET=SECRET_LIVE_DE_PAYPAL
PAYPAL_RETURN_URL=https://tu-dominio.com/orders/payment-done/
PAYPAL_CANCEL_URL=https://tu-dominio.com/orders/payment-cancelled/```

### 🔒 Seguridad

Para el entorno de producción, es **OBLIGATORIO** cambiar estas configuraciones en el archivo `.env`:

```env
# ⚠️ NUNCA True en producción
DEBUG=False

# Dominios permitidos (separados por comas, SIN espacios, SIN corchetes)
ALLOWED_HOSTS=flores.inmerso.io,www.flores.inmerso.io