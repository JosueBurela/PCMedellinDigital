# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class PersonalAdministrativo(AbstractUser):
    AREAS_CHOICES = [
        ('PC', 'Protección Civil'),
        ('IU', 'Imagen Urbana'),
        ('LOG', 'Logística y Operaciones'),
    ]
    
    ROLES_CHOICES = [
        ('SUPER', 'SuperAdmin / Director'),
        ('VALIDADOR', 'Inspector / Validador de Trámites'),
        ('CAPTURISTA', 'Mesa de Control / Capturista'),
    ]

    area = models.CharField(max_length=3, choices=AREAS_CHOICES, default='PC')
    rol_nivel = models.CharField(max_length=15, choices=ROLES_CHOICES, default='CAPTURISTA')
    telefono_institucional = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_rol_nivel_display()}"


class Tramite(models.Model):
    ICON_CHOICES = [
        ('documento', 'Documento / Trámite'),
        ('riesgo', 'Cámara / Reporte de Riesgo'),
        ('maletin', 'Maletín / Comercial'),
        ('operacion', 'Engranaje / Operaciones'),
    ]

    FORM_TYPE_CHOICES = [
        ('GENERAL', 'Carga de Expediente PDF General'),
        ('ANUENCIA_PC', 'Solicitud de Anuencia Protección Civil (Formato 1 de 5)'),
        ('ANUNCIOS_PC', 'Solicitud de Anuencia de Anuncios y Antenas (Formato 2 de 5)'),
        ('CONSTRUCCION_PC', 'Solicitud de Anuencia para Construcción, Remodelación y Demolición (Formato 3 de 5)'),
        ('TERCEROS_PC', 'Registro de Terceros Acreditados y Capacitadores (Formato 4 de 5)'),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    requisitos = models.TextField(blank=True, help_text="Lista de requisitos separados por comas")
    area = models.CharField(max_length=3, choices=PersonalAdministrativo.AREAS_CHOICES, default='PC')
    icono = models.CharField(max_length=20, choices=ICON_CHOICES, default='documento')
    form_type = models.CharField(max_length=30, choices=FORM_TYPE_CHOICES, default='GENERAL')
    sub_tipo = models.CharField(max_length=30, blank=True, null=True, help_text="Subcategoría de trámite (ej. OPERATIVA, RENOVACION, ANUNCIO, etc.)")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    @property
    def requisitos_list(self):
        if not self.requisitos:
            return []
        if '\n' in self.requisitos:
            return [r.strip() for r in self.requisitos.split('\n') if r.strip()]
        elif ';' in self.requisitos:
            return [r.strip() for r in self.requisitos.split(';') if r.strip()]
        return [r.strip() for r in self.requisitos.split(',') if r.strip()]

    def get_style_dict(self):
        if self.area == 'PC':
            return {
                'hover_border': 'hover:border-purple-200',
                'icon_bg': 'bg-purple-50',
                'text': 'text-medellinVino',
                'hover_btn': 'hover:bg-medellinVino hover:text-white hover:border-medellinVino'
            }
        elif self.area == 'IU':
            return {
                'hover_border': 'hover:border-green-200',
                'icon_bg': 'bg-green-50',
                'text': 'text-medellinVerde',
                'hover_btn': 'hover:bg-medellinVerde hover:text-white hover:border-medellinVerde'
            }
        else:
            return {
                'hover_border': 'hover:border-yellow-200',
                'icon_bg': 'bg-yellow-50',
                'text': 'text-medellinOro',
                'hover_btn': 'hover:bg-medellinOro hover:text-white hover:border-medellinOro'
            }

    def __str__(self):
        return self.titulo


class SolicitudTramite(models.Model):
    ESTATUS_CHOICES = [
        ('PENDIENTE', 'Por Validar'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    TIPO_ANUENCIA_CHOICES = [
        ('OPERATIVA', 'Anuencia de operativa de protección civil a instalaciones públicas y privadas'),
        ('RENOVACION', 'Renovación de anuencia operativa'),
        ('RECOMENDACIONES', 'Pliego de Recomendaciones de eventos masivos'),
        ('TEMPORAL', 'Temporal (verificación de seguridad para puestos ambulantes)'),
    ]

    TIPO_ANUENCIA_ANUNCIO_CHOICES = [
        ('ANUNCIO', 'Anuencia de anuncio de Protección Civil'),
        ('ANTENA', 'Anuencia de antena de Protección Civil'),
        ('RENOVACION_ANUNCIO', 'Renovación de anuencia de anuncio de Protección Civil'),
    ]

    TIPO_ANUENCIA_CONSTRUCCION_CHOICES = [
        ('CONSTRUCCION', 'Revisión de planos, proyecto para No inconveniente de construcción'),
        ('REMODELACION', 'Inspección de inmueble y revisión de planos para remodelación y ampliación'),
        ('DEMOLICION', 'Inspección de inmueble a demoler'),
    ]

    TIPO_ANUENCIA_TERCEROS_CHOICES = [
        ('NUEVO_INGRESO', 'Registro de Tercer Acreditado y/o Empresas Capacitadoras e Instructores (Nuevo Ingreso)'),
        ('RENOVACION_REGISTRO', 'Renovación de Registro en el Padrón Municipal'),
    ]

    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='solicitudes')
    ciudadano = models.ForeignKey('Ciudadano', on_delete=models.SET_NULL, blank=True, null=True, related_name='solicitudes')
    establecimiento = models.CharField(max_length=200)
    rfc = models.CharField(max_length=13)
    pdf_documento = models.FileField(upload_to='expedientes/', blank=True, null=True)
    estatus = models.CharField(max_length=15, choices=ESTATUS_CHOICES, default='PENDIENTE')
    creado_en = models.DateTimeField(auto_now_add=True)

    # Campos para la automatización de la Solicitud de Anuencia (Formato 1)
    tipo_anuencia = models.CharField(max_length=30, choices=TIPO_ANUENCIA_CHOICES, default='OPERATIVA', blank=True, null=True)
    propietario_representante = models.CharField(max_length=250, blank=True, null=True)
    unidad_interna_nombre = models.CharField(max_length=250, blank=True, null=True)
    unidad_interna_tel = models.CharField(max_length=15, blank=True, null=True)
    capacidad_fija = models.CharField(max_length=50, blank=True, null=True)
    giro = models.CharField(max_length=150, blank=True, null=True)
    domicilio_calle = models.CharField(max_length=150, blank=True, null=True)
    no_ext = models.CharField(max_length=20, blank=True, null=True)
    no_int = models.CharField(max_length=20, blank=True, null=True)
    entre_calles = models.CharField(max_length=200, blank=True, null=True)
    colonia = models.CharField(max_length=100, blank=True, null=True)
    telefono_contacto = models.CharField(max_length=15, blank=True, null=True)
    horario_funcionamiento = models.CharField(max_length=100, blank=True, null=True)
    superficie_m2 = models.CharField(max_length=50, blank=True, null=True)
    correo_contacto = models.EmailField(blank=True, null=True)

    # Campos específicos para la Solicitud de Anuncios y Antenas (Formato 2)
    tipo_anuencia_anuncio = models.CharField(max_length=30, choices=TIPO_ANUENCIA_ANUNCIO_CHOICES, default='ANUNCIO', blank=True, null=True)
    inspeccion_atiende = models.CharField(max_length=250, blank=True, null=True)

    # Campos específicos para la Solicitud de Construcción, Remodelación y Demolición (Formato 3)
    tipo_anuencia_construccion = models.CharField(max_length=30, choices=TIPO_ANUENCIA_CONSTRUCCION_CHOICES, default='CONSTRUCCION', blank=True, null=True)
    superficie_terreno = models.CharField(max_length=50, blank=True, null=True)
    superficie_construccion = models.CharField(max_length=50, blank=True, null=True)
    realiza_nombre = models.CharField(max_length=250, blank=True, null=True)
    realiza_telefono = models.CharField(max_length=15, blank=True, null=True)
    realiza_correo = models.EmailField(blank=True, null=True)

    # Campos específicos para el Registro de Terceros Acreditados y Capacitadores (Formato 4)
    tipo_anuencia_terceros = models.CharField(max_length=30, choices=TIPO_ANUENCIA_TERCEROS_CHOICES, default='NUEVO_INGRESO', blank=True, null=True)

    # Checkboxes: Documentos presentados (Comunes y Anuncios)
    doc_ine = models.BooleanField(default=False)
    doc_croquis = models.BooleanField(default=False)
    doc_fotos = models.BooleanField(default=False)
    doc_predial = models.BooleanField(default=False)

    # Checkboxes: Requisitos técnicos para emisión (Formato 1)
    req_programa = models.BooleanField(default=False)
    req_corresponsabilidad = models.BooleanField(default=False)
    req_capacitacion = models.BooleanField(default=False)
    req_gas = models.BooleanField(default=False)
    req_electrico = models.BooleanField(default=False)
    req_estructural = models.BooleanField(default=False)
    req_seguro = models.BooleanField(default=False)
    req_pago = models.BooleanField(default=False)

    # Checkboxes: Requisitos técnicos específicos para Anuncios/Antenas (Formato 2)
    req_responsiva_estabilidad = models.BooleanField(default=False)
    req_bitacora_anuncio = models.BooleanField(default=False)
    req_anuencia_vecinos = models.BooleanField(default=False)
    req_analisis_riesgo = models.BooleanField(default=False)

    # Checkboxes: Requisitos específicos para Construcción/Remodelación/Demolición (Formato 3)
    doc_titulo_propiedad = models.BooleanField(default=False)
    req_plano_arquitectonico = models.BooleanField(default=False)
    req_constancia_no_afectacion = models.BooleanField(default=False)
    req_uso_suelo = models.BooleanField(default=False)

    # Checkboxes: Requisitos específicos para Registro de Terceros Acreditados (Formato 4)
    req_cedula_estatal = models.BooleanField(default=False)
    req_curriculum = models.BooleanField(default=False)

    # Archivos Físicos del Expediente
    file_ine = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_croquis = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_fotos = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_predial = models.FileField(upload_to='requisitos/', blank=True, null=True)
    
    # Archivos específicos de Construcción (Formato 3)
    file_titulo_propiedad = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_plano_arquitectonico = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_constancia_no_afectacion = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_uso_suelo = models.FileField(upload_to='requisitos/', blank=True, null=True)
    
    # Archivos específicos de Terceros Acreditados (Formato 4)
    file_cedula_estatal = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_curriculum = models.FileField(upload_to='requisitos/', blank=True, null=True)
    
    file_programa = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_corresponsabilidad = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_capacitacion = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_gas = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_electrico = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_estructural = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_seguro = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_pago = models.FileField(upload_to='requisitos/', blank=True, null=True)
    
    file_responsiva_estabilidad = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_bitacora_anuncio = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_anuencia_vecinos = models.FileField(upload_to='requisitos/', blank=True, null=True)
    file_analisis_riesgo = models.FileField(upload_to='requisitos/', blank=True, null=True)

    class Meta:
        verbose_name = "Solicitud de Trámite"
        verbose_name_plural = "Solicitudes de Trámites"
        indexes = [
            models.Index(fields=['estatus', '-creado_en'], name='idx_solicitud_estatus_fecha'),
            models.Index(fields=['tramite', 'estatus'], name='idx_solicitud_tramite_estatus'),
            models.Index(fields=['ciudadano', '-creado_en'], name='idx_solicitud_ciudadano_fecha'),
            models.Index(fields=['rfc'], name='idx_solicitud_rfc'),
        ]

    def __str__(self):
        return f"{self.establecimiento} - {self.tramite.titulo} ({self.get_estatus_display()})"


class SolicitudAnuenciaPC(SolicitudTramite):
    """Sub-modelo especializado MTI para Solicitudes de Anuencia Protección Civil (Formato 1)"""
    class Meta:
        verbose_name = "Solicitud de Anuencia PC (Formato 1)"
        verbose_name_plural = "Solicitudes de Anuencia PC"


class SolicitudAnunciosPC(SolicitudTramite):
    """Sub-modelo especializado MTI para Solicitudes de Anuncios y Antenas (Formato 2)"""
    class Meta:
        verbose_name = "Solicitud de Anuncio/Antena (Formato 2)"
        verbose_name_plural = "Solicitudes de Anuncios y Antenas"


class SolicitudConstruccionPC(SolicitudTramite):
    """Sub-modelo especializado MTI para Solicitudes de Construcción/Remodelación/Demolición (Formato 3)"""
    class Meta:
        verbose_name = "Solicitud de Construcción (Formato 3)"
        verbose_name_plural = "Solicitudes de Construcción"


class SolicitudTercerosPC(SolicitudTramite):
    """Sub-modelo especializado MTI para Registro de Terceros Acreditados (Formato 4)"""
    class Meta:
        verbose_name = "Solicitud de Tercero Acreditado (Formato 4)"
        verbose_name_plural = "Solicitudes de Terceros Acreditados"


class ReporteRiesgo(models.Model):
    ESTATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente / Sin Atender'),
        ('LEIDO', 'Leído / Evaluando'),
        ('EN_PROCESO', 'En Camino / Atendiendo'),
        ('RESUELTO', 'Finalizado / Resuelto'),
    ]

    SERVICIO_CHOICES = [
        ('GAS', 'Fuga de Gas / Material Peligroso'),
        ('FUEGO', 'Incendio / Conato de Fuego'),
        ('ARBOL', 'Árbol Caído / Obstrucción de Vía'),
        ('AGUA', 'Inundación / Encharcamiento Crítico'),
        ('CABLE', 'Cables Expuestos / Postes Caídos'),
        ('ABEJAS', 'Enjambre de Abejas'),
        ('CHOQUE', 'Accidente Vial / Choque'),
        ('OTRO', 'Otro Incidente de Riesgo'),
    ]

    PRIORIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta / Emergencia'),
    ]

    numero_reporte = models.CharField(max_length=15, unique=True, editable=False)
    ciudadano = models.ForeignKey('Ciudadano', on_delete=models.SET_NULL, blank=True, null=True, related_name='reportes')
    nombre_ciudadano = models.CharField(max_length=150)
    telefono_ciudadano = models.CharField(max_length=10)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    tipo_servicio = models.CharField(max_length=10, choices=SERVICIO_CHOICES, default='OTRO')
    direccion = models.CharField(max_length=255)
    colonia = models.CharField(max_length=100)
    localidad = models.CharField(max_length=100, default='Medellín de Bravo')
    latitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, help_text="Coordenada GPS Latitud")
    longitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, help_text="Coordenada GPS Longitud")
    descripcion = models.TextField()
    evidencia_foto = models.FileField(upload_to='reportes/', blank=True, null=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA')
    leido = models.BooleanField(default=False)
    
    responsables = models.ManyToManyField(PersonalAdministrativo, blank=True, related_name='reportes_atendidos')
    unidad_acudira = models.CharField(max_length=100, blank=True, null=True)
    dependencia_conocimiento = models.CharField(max_length=200, blank=True, null=True)
    tiempo_atencion = models.CharField(max_length=50, blank=True, null=True)
    estatus = models.CharField(max_length=15, choices=ESTATUS_CHOICES, default='PENDIENTE')
    fecha_resolucion = models.DateTimeField(blank=True, null=True)
    
    @property
    def tiempo_resolucion_calculado(self):
        if self.fecha_resolucion:
            diff = self.fecha_resolucion - self.fecha_reporte
            total_seconds = int(diff.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes} min"
        return None

    def save(self, *args, **kwargs):
        if not self.numero_reporte:
            ultimo = ReporteRiesgo.objects.all().order_by('id').last()
            consecutivo = 1 if not ultimo else ultimo.id + 1
            self.numero_reporte = f"REP-{consecutivo:04d}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Reporte de Riesgo"
        verbose_name_plural = "Reportes de Riesgos"
        indexes = [
            models.Index(fields=['estatus', '-fecha_reporte'], name='idx_reporte_estatus_fecha'),
            models.Index(fields=['tipo_servicio', 'estatus'], name='idx_reporte_servicio_estatus'),
            models.Index(fields=['prioridad', 'estatus'], name='idx_reporte_prioridad_estatus'),
            models.Index(fields=['numero_reporte'], name='idx_reporte_folio'),
        ]

    def __str__(self):
        return f"{self.numero_reporte} - {self.get_tipo_servicio_display()} ({self.get_estatus_display()})"


class Ciudadano(models.Model):
    correo = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=10)
    curp = models.CharField(max_length=18, unique=True, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=10, blank=True, null=True) # Hombre / Mujer
    estado_nacimiento = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=128, default="") # Hash encriptado seguro (PBKDF2/SHA256)
    codigo_2fa = models.CharField(max_length=6, blank=True, null=True) # Código OTP de 6 dígitos
    codigo_2fa_expiracion = models.DateTimeField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.correo} - {self.nombre} {self.primer_apellido}"


class HistorialReporte(models.Model):
    reporte = models.ForeignKey(ReporteRiesgo, on_delete=models.CASCADE, related_name='historial')
    creado_por = models.ForeignKey(PersonalAdministrativo, on_delete=models.SET_NULL, null=True)
    comentario = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reporte.numero_reporte} - {self.fecha_registro.strftime('%d/%m/%Y %H:%M')}"


class MensajeChat(models.Model):
    solicitud = models.ForeignKey(SolicitudTramite, on_delete=models.CASCADE, related_name='mensajes_chat', blank=True, null=True)
    reporte = models.ForeignKey(ReporteRiesgo, on_delete=models.CASCADE, related_name='mensajes_chat', blank=True, null=True)
    remitente_ciudadano = models.ForeignKey(Ciudadano, on_delete=models.CASCADE, blank=True, null=True)
    remitente_admin = models.ForeignKey(PersonalAdministrativo, on_delete=models.CASCADE, blank=True, null=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        dest = f"Solicitud {self.solicitud.id}" if self.solicitud else f"Reporte {self.reporte.id}"
        if self.remitente_ciudadano:
            sender = self.remitente_ciudadano.nombre
        elif self.remitente_admin:
            sender = f"{self.remitente_admin.username} (Admin)"
        else:
            sender = "Ciudadano (Público)"
        return f"{dest} - {sender}: {self.mensaje[:25]}"


class Localidad(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ActividadGiro(models.Model):
    numero = models.IntegerField(unique=True)
    actividad = models.CharField(max_length=255)
    riesgo = models.CharField(max_length=50) # 'Bajo Riesgo', 'Mediano Riesgo', 'Alto Riesgo'

    class Meta:
        verbose_name = "Actividad y Giro de Riesgo"
        verbose_name_plural = "Actividades y Giros de Riesgo"
        ordering = ['numero']

    def __str__(self):
        return f"{self.numero} - {self.actividad} ({self.riesgo})"


class Trabajador(models.Model):
    CATEGORIA_CHOICES = [
        ('BOMBERO', 'Bomberos'),
        ('AMBULANCIA', 'Ambulancias / Paramédicos'),
        ('POLICIA', 'Policía Municipal'),
    ]

    TURNO_CHOICES = [
        ('TURNO_1', 'Turno 1 (00:00 - 12:00)'),
        ('TURNO_2', 'Turno 2 (12:00 - 00:00)'),
    ]

    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, help_text="Formato WhatsApp (ej. 5212291234567)")
    categoria = models.CharField(max_length=15, choices=CATEGORIA_CHOICES)
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES, default='TURNO_1')
    numero_empleado = models.CharField(max_length=20, unique=True, blank=True, help_text="Folio asignado automáticamente ej. BOM-0001")
    password = models.CharField(max_length=128, blank=True, default="", help_text="Contraseña encriptada para acceso a la App Móvil")
    is_active = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Trabajador de Emergencia"
        verbose_name_plural = "Trabajadores de Emergencia"
        ordering = ['nombre']

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # Limpiar caracteres no numéricos
        num_limpio = ''.join(c for c in self.telefono if c.isdigit())
        
        # Si tiene 10 dígitos (número celular mexicano estándar), anteponer 521
        if len(num_limpio) == 10:
            self.telefono = f"521{num_limpio}"
        else:
            self.telefono = num_limpio

        # Auto-generar numero_empleado si no tiene uno asignado
        if not self.numero_empleado:
            prefix_map = {
                'BOMBERO': 'BOM',
                'AMBULANCIA': 'AMB',
                'POLICIA': 'POL',
            }
            prefijo = prefix_map.get(self.categoria, 'EMP')
            
            # Contar existentes en esa categoría para el consecutivo
            existentes = Trabajador.objects.filter(numero_empleado__startswith=f"{prefijo}-")
            count = existentes.count() + 1
            nuevo_codigo = f"{prefijo}-{count:04d}"
            
            # Garantizar unicidad
            while Trabajador.objects.filter(numero_empleado=nuevo_codigo).exists():
                count += 1
                nuevo_codigo = f"{prefijo}-{count:04d}"
            
            self.numero_empleado = nuevo_codigo
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_empleado or 'N/A'} - {self.nombre} ({self.get_categoria_display()})"


class PlantillaGuardia(models.Model):
    JORNADA_CHOICES = [
        ('24H', 'Jornada de 24 Horas'),
        ('12H_M', 'Jornada 12 Horas (Día)'),
        ('12H_N', 'Jornada 12 Horas (Noche)'),
        ('ESPECIAL', 'Operativo Especial / Relevo'),
    ]

    nombre = models.CharField(max_length=150)
    jornada_tipo = models.CharField(max_length=15, choices=JORNADA_CHOICES, default='24H')
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, default="#5A123E")
    trabajadores = models.ManyToManyField(Trabajador, related_name='plantillas', blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plantilla de Guardia"
        verbose_name_plural = "Plantillas de Guardias"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_jornada_tipo_display()})"


class ProgramacionGuardia(models.Model):
    fecha = models.DateField(unique=True)
    plantilla = models.ForeignKey(PlantillaGuardia, on_delete=models.CASCADE, related_name='programaciones')
    notas = models.CharField(max_length=255, blank=True, null=True)
    creado_por = models.ForeignKey(PersonalAdministrativo, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Programación de Guardia"
        verbose_name_plural = "Programaciones de Guardias"
        ordering = ['fecha']

    def __str__(self):
        return f"{self.fecha.strftime('%d/%m/%Y')} -> {self.plantilla.nombre}"


class SesionAtencionWhatsApp(models.Model):
    phone_number = models.CharField(max_length=30, unique=True)
    reporte = models.ForeignKey(ReporteRiesgo, on_delete=models.CASCADE)
    paso = models.IntegerField(default=1)  # 1: esperando unidad, 2: esperando tiempo de atención
    unidad_acudira = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sesión de Atención WhatsApp"
        verbose_name_plural = "Sesiones de Atención WhatsApp"

    def __str__(self):
        return f"{self.phone_number} -> {self.reporte.numero_reporte} (Paso {self.paso})"


class RolGuardiaFirmado(models.Model):
    GUARDIA_CHOICES = [
        ('GUARDIA_1', 'Guardia 1'),
        ('GUARDIA_2', 'Guardia 2'),
        ('GUARDIA_3', 'Guardia 3'),
        ('GENERAL', 'Rol Completo (Guardias 1 y 2)'),
    ]

    fecha_periodo = models.DateField(default=timezone.now)
    guardia_tipo = models.CharField(max_length=20, choices=GUARDIA_CHOICES, default='GENERAL')
    comandante_nombre = models.CharField(max_length=150, blank=True, null=True)
    observaciones_novedades = models.TextField(blank=True, null=True)
    imagen_documento_firmado = models.FileField(upload_to='roles_guardia/')
    subido_por = models.ForeignKey(PersonalAdministrativo, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rol de Guardia Firmado"
        verbose_name_plural = "Roles de Guardias Firmados"
        ordering = ['-fecha_periodo', '-creado_en']

    def __str__(self):
        return f"Rol Firmado ({self.fecha_periodo.strftime('%d/%m/%Y')}) - {self.get_guardia_tipo_display()}"


class RolGuardiaConfigurado(models.Model):
    GUARDIA_CHOICES = [
        ('GUARDIA_1', 'Guardia 1'),
        ('GUARDIA_2', 'Guardia 2'),
        ('GENERAL', 'Rol Completo (Guardias 1 y 2)'),
    ]

    fecha = models.DateField(unique=True)
    guardia_tipo = models.CharField(max_length=20, choices=GUARDIA_CHOICES, default='GENERAL')
    comandante_g1 = models.CharField(max_length=150, blank=True, null=True, default='Comandante / Jefe de Guardia')
    comandante_g2 = models.CharField(max_length=150, blank=True, null=True, default='Comandante / Jefe de Guardia')
    datos_json = models.TextField(default='{}')
    creado_por = models.ForeignKey(PersonalAdministrativo, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rol de Guardia Configurado"
        verbose_name_plural = "Roles de Guardias Configurados"
        ordering = ['-fecha']

    def __str__(self):
        return f"Rol Configurado ({self.fecha.strftime('%d/%m/%Y')})"



# ==============================================================================
#  🛠️ SUITE DE HERRAMIENTAS AUXILIARES Y APPS EXTERNAS
# ==============================================================================

class ContactoDirectorio(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)
    empresa = models.CharField(max_length=150, blank=True, null=True)
    puesto = models.CharField(max_length=150, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    web = models.CharField(max_length=150, blank=True, null=True)
    foto = models.ImageField(upload_to='directorio/', blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contacto de Directorio"
        verbose_name_plural = "Contactos de Directorio"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.puesto or 'Contacto'})"


class OrdenInspeccion(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Completado', 'Completado'),
    ]

    fecha_corta = models.DateField()
    fecha_texto = models.CharField(max_length=150)
    horario = models.CharField(max_length=100, default='De 10am A 2pm')
    rutas_resumen = models.CharField(max_length=255)
    inspector = models.CharField(max_length=150)
    operador = models.CharField(max_length=150)
    director = models.CharField(max_length=150, default='L.E.D. DANIEL EDUARDO ROMERO PILAR')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Orden de Inspección"
        verbose_name_plural = "Órdenes de Inspecciones"
        ordering = ['-fecha_corta', '-id']

    def __str__(self):
        return f"Orden #{self.id} ({self.fecha_corta}) - Inspector: {self.inspector}"


class ItemInspeccion(models.Model):
    orden = models.ForeignKey(OrdenInspeccion, related_name='items', on_delete=models.CASCADE)
    numero = models.IntegerField(default=1)
    ruta = models.CharField(max_length=150)
    establecimiento = models.CharField(max_length=255)
    mes_pago = models.CharField(max_length=50, blank=True, default='')
    realizado = models.CharField(max_length=50, blank=True, default='')
    pendiente = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        verbose_name = "Ítem de Inspección"
        verbose_name_plural = "Ítems de Inspección"
        ordering = ['numero']

    def __str__(self):
        return f"Item #{self.numero} ({self.ruta}) - {self.establecimiento}"


class ConfiguracionInspeccion(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()

    class Meta:
        verbose_name = "Configuración de Inspección"
        verbose_name_plural = "Configuraciones de Inspección"

    def __str__(self):
        return f"{self.key}: {self.value[:30]}"


class FichaInformativa(models.Model):
    TIPO_CHOICES = [
        ('OFICIO', 'Oficio Municipal / Solicitud'),
        ('TARJETA_INFORMATIVA', 'Tarjeta Informativa de Emergencias / Hechos'),
    ]

    tipo_documento = models.CharField(max_length=30, choices=TIPO_CHOICES, default='OFICIO')
    num_oficio = models.CharField(max_length=150, blank=True, null=True)
    asunto = models.CharField(max_length=255)
    lugar_fecha = models.CharField(max_length=200)
    
    # Campos especificos de Tarjeta Informativa
    hora_reporte = models.CharField(max_length=50, blank=True, null=True)
    hora_arribo = models.CharField(max_length=50, blank=True, null=True)
    lugar_hechos = models.TextField(blank=True, null=True)

    # Campos especificos de Oficio
    destinatario_nombre = models.CharField(max_length=200, blank=True, null=True)
    destinatario_cargo = models.CharField(max_length=200, blank=True, null=True)
    destinatario_dependencia = models.CharField(max_length=200, blank=True, null=True)
    atencion_nombre = models.CharField(max_length=200, blank=True, null=True)
    atencion_cargo = models.CharField(max_length=200, blank=True, null=True)
    
    cuerpo_texto = models.TextField()
    firmante_nombre = models.CharField(max_length=200, default='LIC. DANIEL EDUARDO ROMERO PILAR')
    firmante_cargo = models.TextField(default='TITULAR DE LA UNIDAD MUNICIPAL DE PROTECCIÓN CIVIL Y BOMBEROS DEL H. AYUNTAMIENTO MEDELLÍN DE BRAVO, VER.')
    ccp_lineas = models.TextField(blank=True, null=True, default='C.c. p -. Presidencia\nC.c.p -. Archivo')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ficha Informativa / Oficio"
        verbose_name_plural = "Fichas Informativas y Oficios"
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.asunto[:30]}"


# ==============================================================================
# 🚑 MÓDULO CONTROL DE VEHÍCULOS & BITÁCORA DIGITAL DE EMERGENCIAS
# ==============================================================================

class VehiculoUnidad(models.Model):
    TIPO_CHOICES = [
        ('Ambulancia', 'Ambulancia'),
        ('Pipa', 'Pipa de Agua'),
        ('PickUp', 'Pick Up / Camioneta Operativa'),
        ('Rescate', 'Unidad de Rescate'),
        ('Moto', 'Motocicleta Operativa'),
        ('Bomberos', 'Camión de Bomberos'),
    ]

    ESTATUS_CHOICES = [
        ('DISPONIBLE', '🟢 Disponible'),
        ('EN_SERVICIO', '🔴 En Servicio (No Disponible)'),
        ('MANTENIMIENTO', '🛠️ En Mantenimiento'),
        ('FUERA_DE_SERVICIO', '⚠️ Fuera de Servicio'),
    ]

    GASOLINA_CHOICES = [
        ('Reserva', '⚠️ Reserva (Bajo)'),
        ('1/4', '1/4 de Tanque'),
        ('1/2', '1/2 de Tanque'),
        ('3/4', '3/4 de Tanque'),
        ('Lleno', '⛽ Tanque Lleno'),
    ]

    numero_unidad = models.CharField(max_length=50, unique=True, help_text="Ej. 208, 072, 096")
    nombre_identificador = models.CharField(max_length=150, help_text="Ej. Ambulancia 208, Pipa 072")
    tipo_vehiculo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='Ambulancia')
    placas = models.CharField(max_length=50, blank=True, null=True, help_text="Placas de la unidad")
    foto_unidad = models.ImageField(upload_to='vehiculos/fotos/', blank=True, null=True)
    
    estatus = models.CharField(max_length=30, choices=ESTATUS_CHOICES, default='DISPONIBLE')
    odometro_actual = models.PositiveIntegerField(default=0, help_text="Kilometraje actual del odómetro")
    nivel_gasolina_actual = models.CharField(max_length=30, choices=GASOLINA_CHOICES, default='Lleno')
    latitud_base = models.DecimalField(max_digits=10, decimal_places=7, default=19.0558, help_text="Coordenada GPS Latitud de Base")
    longitud_base = models.DecimalField(max_digits=10, decimal_places=7, default=-96.1558, help_text="Coordenada GPS Longitud de Base")
    
    ultima_salida_finalizada = models.DateTimeField(blank=True, null=True, help_text="Fecha y hora del último retorno a base")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vehículo de Flotilla"
        verbose_name_plural = "Vehículos de Flotilla"
        ordering = ['numero_unidad']

    def __str__(self):
        return f"{self.nombre_identificador} ({self.get_estatus_display()})"

    def save(self, *args, **kwargs):
        if self.foto_unidad:
            try:
                from PIL import Image
                from io import BytesIO
                from django.core.files.uploadedfile import InMemoryUploadedFile

                if hasattr(self.foto_unidad, 'file') and self.foto_unidad.file:
                    img = Image.open(self.foto_unidad)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    output = BytesIO()
                    img.save(output, format='JPEG', quality=80, optimize=True)
                    output.seek(0)
                    self.foto_unidad.file = InMemoryUploadedFile(
                        output, 'ImageField',
                        f"{self.foto_unidad.name.split('.')[0]}.jpg",
                        'image/jpeg', output.getbuffer().nbytes, None
                    )
            except Exception:
                pass
        super().save(*args, **kwargs)

    def horas_sin_uso(self):
        if not self.ultima_salida_finalizada:
            return None
        diff = timezone.now() - self.ultima_salida_finalizada
        return round(diff.total_seconds() / 3600, 1)


class BitacoraSalidaVehiculo(models.Model):
    unidad = models.ForeignKey(VehiculoUnidad, on_delete=models.CASCADE, related_name='salidas')
    operador_nombre = models.CharField(max_length=200, help_text="Nombre del operador o paramédico a cargo")
    guardia_turno = models.CharField(max_length=100, blank=True, null=True, help_text="Ej. Paco / Guardia 1")
    descripcion_servicio = models.TextField(help_text="Motivo / Descripción del servicio o llamada de emergencia")
    
    fecha_salida = models.DateTimeField(default=timezone.now)
    odometro_salida = models.PositiveIntegerField(help_text="Kilometraje al salir")
    gasolina_salida = models.CharField(max_length=30, choices=VehiculoUnidad.GASOLINA_CHOICES, default='Lleno')
    foto_odometro_salida = models.ImageField(upload_to='vehiculos/odometros_salida/', blank=True, null=True)
    foto_gasolina_salida = models.ImageField(upload_to='vehiculos/gasolina_salida/', blank=True, null=True)
    
    incongruencia_salida = models.BooleanField(default=False)
    detalle_incongruencia_salida = models.CharField(max_length=255, blank=True, null=True)

    fecha_llegada = models.DateTimeField(blank=True, null=True)
    odometro_llegada = models.PositiveIntegerField(blank=True, null=True)
    gasolina_llegada = models.CharField(max_length=30, choices=VehiculoUnidad.GASOLINA_CHOICES, blank=True, null=True)
    foto_odometro_llegada = models.ImageField(upload_to='vehiculos/odometros_llegada/', blank=True, null=True)
    foto_gasolina_llegada = models.ImageField(upload_to='vehiculos/gasolina_llegada/', blank=True, null=True)
    
    km_recorridos = models.PositiveIntegerField(default=0, help_text="Calculado: Odómetro Llegada - Odómetro Salida")
    duracion_minutos = models.PositiveIntegerField(default=0)
    completado = models.BooleanField(default=False)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de Bitácora de Salida"
        verbose_name_plural = "Registros de Bitácora de Salidas"
        ordering = ['-fecha_salida']

    def __str__(self):
        estado_str = "FINALIZADO" if self.completado else "EN CURSO"
        return f"{self.unidad.nombre_identificador} - {self.operador_nombre} ({estado_str})"


class RegistroCargaGasolina(models.Model):
    unidad = models.ForeignKey(VehiculoUnidad, on_delete=models.CASCADE, related_name='cargas_gasolina')
    operador = models.CharField(max_length=200, help_text="Nombre de quien realizó la carga")
    fecha_carga = models.DateTimeField(default=timezone.now)
    litros_cargados = models.DecimalField(max_digits=8, decimal_places=2, help_text="Litros surtidos")
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Importe total en $ MXN")
    odometro_al_cargar = models.PositiveIntegerField(help_text="Kilometraje al momento de cargar")
    foto_ticket_o_bomba = models.ImageField(upload_to='vehiculos/tickets_gasolina/', blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Carga de Gasolina"
        verbose_name_plural = "Cargas de Gasolina"
        ordering = ['-fecha_carga']

    def __str__(self):
        return f"{self.unidad.nombre_identificador} - {self.litros_cargados}L (${self.costo_total})"


class UsuarioOperadorVehiculo(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', '🕒 Pendiente de Aprobación'),
        ('APROBADO', '🟢 Activo / Aprobado'),
        ('DESACTIVADO', '🔴 Desactivado / Suspendido'),
        ('RECHAZADO', '❌ Rechazado'),
    ]

    ROL_CHOICES = [
        ('OPERADOR', 'Operador / Paramédico'),
        ('ADMIN', 'Administrador de Flotilla'),
    ]

    nombre_completo = models.CharField(max_length=200, unique=True, help_text="Nombre completo (se guarda en MAYÚSCULAS)")
    password_hash = models.CharField(max_length=256)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='OPERADOR')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Operador de Vehículo"
        verbose_name_plural = "Operadores de Vehículos"
        ordering = ['nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} ({self.get_estado_display()})"

    def save(self, *args, **kwargs):
        if self.nombre_completo:
            self.nombre_completo = self.nombre_completo.strip().upper()
        super().save(*args, **kwargs)


# ==============================================================================
#  🎓 MÓDULO DE CAPACITACIONES Y CONSTANCIAS AUTOMATIZADAS
# ==============================================================================

class CursoCapacitacion(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título del Curso / Capacitación")
    descripcion = models.TextField(verbose_name="Descripción y Temario del Curso")
    duracion_horas = models.PositiveIntegerField(default=8, verbose_name="Duración en Horas")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio / Impartición")
    fecha_fin = models.DateField(blank=True, null=True, verbose_name="Fecha de Finalización (Opcional)")
    horario = models.CharField(max_length=100, default="09:00 a 14:00 hrs", verbose_name="Horario")
    sede_ubicacion = models.CharField(max_length=200, default="Estación Central de Bomberos El Tejar", verbose_name="Sede / Ubicación")
    cupo_maximo = models.PositiveIntegerField(default=50, verbose_name="Cupo Máximo de Participantes")
    activo = models.BooleanField(default=True, verbose_name="¿Curso Activo para Registro Público?")
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Curso de Capacitación"
        verbose_name_plural = "Cursos de Capacitación"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio.strftime('%d/%m/%Y')})"


class InscripcionCapacitacion(models.Model):
    curso = models.ForeignKey(CursoCapacitacion, on_delete=models.CASCADE, related_name='inscritos')
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo (tal como aparecerá en Constancia)")
    curp = models.CharField(max_length=18, blank=True, null=True, verbose_name="CURP (Opcional)")
    correo = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono / WhatsApp")
    empresa_institucion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Empresa / Institución Solicitante")
    
    asistio = models.BooleanField(default=False, verbose_name="¿Asistió al Curso?")
    aprobado = models.BooleanField(default=False, verbose_name="¿Aprobó y Cumplió Requisitos?")
    
    folio_constancia = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Folio Único de Constancia")
    codigo_qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_emision = models.DateTimeField(blank=True, null=True, verbose_name="Fecha y Hora de Emisión de Constancia")

    class Meta:
        verbose_name = "Inscripción a Capacitación"
        verbose_name_plural = "Inscripciones a Capacitaciones"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre_completo} - {self.curso.titulo}"

    def save(self, *args, **kwargs):
        if self.nombre_completo:
            self.nombre_completo = self.nombre_completo.strip().upper()
        if self.curp:
            self.curp = self.curp.strip().upper()
        if self.empresa_institucion:
            self.empresa_institucion = self.empresa_institucion.strip().upper()
            
        # Generar folio único automático si no existe
        if not self.folio_constancia:
            ultimo = InscripcionCapacitacion.objects.filter(folio_constancia__isnull=False).count() + 1
            year = timezone.now().year
            self.folio_constancia = f"CONST-{year}-PC-{ultimo:04d}"
            
        super().save(*args, **kwargs)








