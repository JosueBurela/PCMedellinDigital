# Walkthrough - App Móvil Exclusiva de Trabajadores de Campo & Centro de Descarga APK

Se ha desarrollado e implementado con éxito la **App Móvil Exclusiva para Trabajadores de Campo** (Bomberos, Paramédicos y Policía Municipal) de Protección Civil Medellín de Bravo, junto con la plataforma web de descarga del paquete `.apk` directamente desde el servidor.

---

## 🎯 Resumen de Funcionalidades Desarrolladas

### 1. Centro Web de Descarga de APK (`/descargar-app/`)
- **Página Institucional**: Interfaz web táctil moderna con estética premium (vino/oscuro institucional).
- **Servidor de Archivos**: Endpoint binario `/descargar-app/apk/` que sirve directamente el paquete `ProteccionCivilMedellin_Campo.apk` almacenado en la carpeta `media/app/` de tu servidor.
- **Código QR Dinámico**: Los usuarios en PC pueden escanear el código QR directamente con la cámara de su celular para iniciar la descarga inmediata.
- **Guía de Instalación Android**: Instrucciones paso a paso para habilitar "Permitir desde esta fuente" en teléfonos Android.

---

### 2. Auto-Registro con Número de Empleado Correlativo (`/campo/registro/`)
- **Asignación Automática de Folio de Empleado**:
  - **Bomberos**: Genera folios secuenciales `BOM-0001`, `BOM-0002`, ...
  - **Ambulancias / Paramédicos**: Genera folios secuenciales `AMB-0001`, `AMB-0002`, ...
  - **Policía Municipal**: Genera folios secuenciales `POL-0001`, `POL-0002`, ...
- **Almacenamiento de Teléfono para el Administrador**: Guarda el número telefónico del elemento para que la dirección municipal pueda contactarlo o llamarle directamente en cualquier momento.
- **Credencial Digital**: Tras registrarse, se despliega una tarjeta de confirmación con su nuevo Número de Empleado y un botón para acceder a la app.

---

### 3. Acceso y Portal Móvil Operativo (`/campo/login/` & `/campo/dashboard/`)
- **Inicio de Sesión**: Los elementos ingresan únicamente con su **Número de Empleado** (ej. `BOM-0001`) y su **Contraseña**.
- **Alertas de Emergencia en Turno**:
  - Detecta si el trabajador está en la guardia activa del día.
  - Reproduce **sonido de sirena de emergencia** y notificaciones emergentes al registrarse reportes de riesgo.
- **Atención de Servicios en Campo**:
  - Enlaces directos para abrir la ubicación en **Google Maps** o Waze.
  - Botón táctil **"Atender Alerta"** para marcar la salida de la unidad en tiempo real.

---

### 4. Actualización del Panel de Administración (`/panel/`)
- El directorio de personal en la consola web administrativa incluye las insignias con el **Número de Empleado** asignado (`BOM-0001`, `AMB-0001`, `POL-0001`) y enlace directo para llamadas telefónicas (`tel:`).

---

## 🔬 Verificación y Pruebas Realizadas

1. **System Check de Django**:
   - `python manage.py check` -> 0 errores.
2. **Migración de Base de Datos**:
   - Aplicada migración `portal.0030_trabajador_is_active_trabajador_numero_empleado_and_more`.
3. **Prueba de Auto-Registro y Hash de Contraseñas**:
   - Registrado Bombero de prueba -> Folio asignado `BOM-0001`.
   - Registrada Paramédico de prueba -> Folio asignado `AMB-0001`.
   - Verificada la autenticación segura mediante `check_password()`.
4. **Prueba de Rutas HTTP**:
   - `/descargar-app/` -> HTTP 200 OK.
   - `/descargar-app/apk/` -> HTTP 200 OK (`Content-Type: application/vnd.android.package-archive`).
   - `/campo/registro/` -> HTTP 200 OK.
   - `/campo/login/` -> HTTP 200 OK.
