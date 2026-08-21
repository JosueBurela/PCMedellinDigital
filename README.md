# Sistema Digital de Protección Civil y Bomberos
## H. Ayuntamiento de Medellín de Bravo, Veracruz (2026–2029)

Plataforma web integral para la gestión operativa, atención de emergencias ciudadanas, control de flotilla vehicular y geolocalización GIS en tiempo real de la Dirección de Protección Civil y Bomberos de Medellín de Bravo, Veracruz.

---

## Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Módulos del Sistema](#módulos-del-sistema)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Arquitectura e Infraestructura](#arquitectura-e-infraestructura)
- [Instalación y Configuración Local](#instalación-y-configuración-local)
- [Despliegue en Producción](#despliegue-en-producción)
- [Autor y Créditos](#autor-y-créditos)

---

## Descripción General

El **Sistema Digital de Protección Civil y Bomberos** es una solución gubernamental diseñada para optimizar los tiempos de respuesta ante contingencias urbanas y rurales en el municipio de Medellín de Bravo. Permite a la ciudadanía reportar situaciones de riesgo en tiempo real con transmisión de coordenadas GPS y evidencia fotográfica, al tiempo que proporciona a los mandos operativos un centro de control GIS en tiempo real y una bitácora digital de control vehicular.

---

## Módulos del Sistema

### 1. Portal Ciudadano y Reporte de Riesgos
- **Formulario Inteligente**: Permite el registro de incidentes (fugas de gas, incendios, enjambres de abejas, inundaciones, accidentes viales).
- **Geolocalización GPS**: Captura de coordenadas precisas mediante la API HTML5 Geolocation.
- **Autocompletado de Colonias y Localidades**: Catálogo desduplicado y estructurado del municipio.
- **Evidencia Fotográfica**: Carga directa de imágenes con compresión y optimización automática.

### 2. Centro de Mando GIS en Tiempo Real
- **Mapa Interactivo (Leaflet.js / OpenStreetMap)**: Visualización en tiempo real de emergencias activas y posición de unidades.
- **Simbología por Categorías**: Marcadores diferenciados por tipo de emergencia con código de colores.
- **Actualización Asíncrona (AJAX)**: Sondeo cada 15 segundos para refresco de incidentes en vivo sin recargar página.
- **Popups de Detalle**: Consulta de evidencia, contacto del ciudadano y estatus de atención.

### 3. Control de Flotilla Vehicular y Bitácora Digital
- **Gestión Aislada de Operadores**: Autenticación y control de acceso para personal de guardia y administradores.
- **Registro de Salidas y Retornos**: Captura de odómetro, nivel de combustible y observaciones.
- **Detección Automática de Incongruencias**: Verificación de kilometraje entre turnos con marcado de alertas.
- **Evidencia Fotográfica Obligatoria**: Verificación doble de fotos (tablero/odómetro e indicador de combustible).
- **Expediente e Historial por Unidad**: Consulta cronológica inversa de servicios realizados y recargas de combustible.
- **PWA (Progressive Web App)**: Configuración en modo *standalone* instalable en dispositivos móviles sin barra de navegación.

### 4. Herramientas Auxiliares Institucionales
- **Generador de Órdenes de Inspección**: Emisión de documentos oficiales imprimibles para verificación de giros comerciales y construcciones.
- **Generador de Fichas Informativas**: Reportes ejecutivos estandarizados para mandos superiores.

### 5. Integración con WhatsApp Bot / Webhook
- **Alertas Automáticas**: Notificación inmediata a grupos operativos al generarse un reporte crítico.
- **Consulta de Estado**: Endpoint interactivo para seguimiento de folios desde WhatsApp.

---

## Tecnologías Utilizadas

- **Backend**: Python 3.12, Django 5.x / 6.x
- **Frontend**: HTML5, Tailwind CSS, JavaScript (ES6+), Leaflet.js
- **Iconografía y Estilos**: Lucide Vector Icons, Inter Font
- **Procesamiento de Imágenes**: Pillow (PIL) con optimización JPEG (Resampling LANCZOS)
- **Servidor y Proxy**: Nginx 1.24, Gunicorn
- **Seguridad y SSL**: Certbot (Let's Encrypt TLS/SSL)

---

## Arquitectura e Infraestructura

```
PCivil Digital /
├── core/                   # Configuración global del proyecto Django (settings, urls, wsgi)
├── portal/                 # Aplicación principal
│   ├── models.py           # Modelos de datos (ReporteRiesgo, VehiculoUnidad, Bitacora, etc.)
│   ├── views/              # Controladores modularizados (auth, reportes, vehiculos, mapa, etc.)
│   ├── templates/portal/   # Plantillas HTML5 con Tailwind CSS
│   ├── static/portal/      # Archivos estáticos (imágenes, manifest.json)
│   └── migrations/         # Migraciones de base de datos
├── media/                  # Almacenamiento de archivos multimedia subidos
├── staticfiles/            # Archivos estáticos recolectados para producción
└── manage.py
```

---

## Instalación y Configuración Local

### Prerrequisitos
- Python 3.10 o superior
- Git

### Pasos de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/JosueBurela/PCMedellinDigital.git
   cd PCMedellinDigital
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
   *(En caso de no contar con `requirements.txt`, instalar: `pip install django pillow requests gunicorn`)*

4. **Ejecutar migraciones de la base de datos:**
   ```bash
   python manage.py migrate
   ```

5. **Iniciar el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```
   Acceder en el navegador a: `http://127.0.0.1:8000/`

---

## Despliegue en Producción

El sistema está configurado para desplegarse sobre Ubuntu Linux utilizando Gunicorn como servidor WSGI y Nginx como proxy inverso.

### Comandos de actualización en servidor:

```bash
cd /var/www/pcivildigital
git pull origin main
./venv/bin/python manage.py migrate
./venv/bin/python manage.py collectstatic --noinput --clear
systemctl restart gunicorn
```

### Configuración Nginx (`/etc/nginx/sites-available/default`):

```nginx
server {
    server_name 162-243-15-87.sslip.io 162.243.15.87;
    client_max_body_size 50M;

    location /static/ {
        alias /var/www/pcivildigital/staticfiles/;
    }

    location /media/ {
        alias /var/www/pcivildigital/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Autor y Créditos

- **Desarrollo y Diseño de Software**: Josué Jaziel Delgado Burela
- **Institución**: H. Ayuntamiento de Medellín de Bravo, Veracruz
- **Contacto**: `jburela1@gmail.com`
- **Copyright**: © 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
