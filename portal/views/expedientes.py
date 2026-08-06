# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.http import HttpResponse
import datetime
from portal.models import PersonalAdministrativo, Tramite, SolicitudTramite, ReporteRiesgo, Ciudadano, HistorialReporte, MensajeChat, Trabajador, PlantillaGuardia, ProgramacionGuardia
from portal.utils import parsear_curp




# Vista de Acceso Unificado para Ciudadanos y Personal Administrativo




# Registro Paso 1: Ingreso y decodificación de la CURP

# Registro Paso 2: Datos de contacto y Contraseña


@login_required(login_url='login_unificado')
def dashboard_admin(request):
    personal = request.user
    seccion = request.GET.get('seccion', 'resumen')
    
    contexto = {
        'personal': personal,
        'area': personal.get_area_display(),
        'rol': personal.rol_nivel,
        'seccion': seccion,
    }
        # Carga de solicitudes/expedientes pendientes de validación
    if personal.rol_nivel in ['SUPER', 'VALIDADOR']:
        # Validar si se está enfocando en una solicitud para ver su chat y detalles
        ver_solicitud_id = request.GET.get('ver_solicitud')
        if ver_solicitud_id and ver_solicitud_id.isdigit():
            solicitud_obj = get_object_or_404(SolicitudTramite.objects.select_related('tramite', 'ciudadano'), id=ver_solicitud_id)
            contexto['solicitud_enfocada'] = solicitud_obj
            contexto['chat_mensajes'] = solicitud_obj.mensajes_chat.all().select_related('remitente_admin').order_by('fecha_envio')
 
        if personal.rol_nivel == 'SUPER':
            qs = SolicitudTramite.objects.filter(estatus='PENDIENTE').select_related('tramite', 'ciudadano').order_by('-creado_en')
            contexto['expedientes_pendientes'] = qs
            contexto['total_pendientes'] = qs.count()
        else:
            qs = SolicitudTramite.objects.filter(estatus='PENDIENTE', tramite__area=personal.area).select_related('tramite', 'ciudadano').order_by('-creado_en')
            contexto['expedientes_pendientes'] = qs
            contexto['total_pendientes'] = qs.count()
            
    # Carga de Reportes de Riesgo (SUPER / VALIDADOR / CAPTURISTA)
    if seccion == 'reportes':
        # Validar si se está enfocando en un reporte específico para la Bitácora
        ver_reporte_id = request.GET.get('ver_reporte')
        if ver_reporte_id and ver_reporte_id.isdigit():
            reporte_obj = get_object_or_404(ReporteRiesgo, id=ver_reporte_id)
            contexto['reporte_enfocado'] = reporte_obj
            if reporte_obj.estatus == 'PENDIENTE':
                reporte_obj.estatus = 'LEIDO'
                reporte_obj.leido = True
                reporte_obj.save()
                HistorialReporte.objects.create(
                    reporte=reporte_obj,
                    creado_por=personal,
                    comentario="El administrador ha recibido su reporte y está coordinando la asignación de la unidad pertinente para atender su caso."
                )
            contexto['bitacora_list'] = reporte_obj.historial.all().order_by('-fecha_registro')
            contexto['chat_mensajes'] = reporte_obj.mensajes_chat.all().order_by('fecha_envio')
            
        # Filtros Combinados (GET)
        f_prioridad = request.GET.get('f_prioridad', '').strip()
        f_tipo = request.GET.get('f_tipo', '').strip()
        f_estatus = request.GET.get('f_estatus', '').strip()
        f_ubicacion = request.GET.get('f_ubicacion', '').strip()
        
        reportes_qs = ReporteRiesgo.objects.all()
        
        if f_prioridad:
            reportes_qs = reportes_qs.filter(prioridad=f_prioridad)
        if f_tipo:
            reportes_qs = reportes_qs.filter(tipo_servicio=f_tipo)
        if f_estatus:
            reportes_qs = reportes_qs.filter(estatus=f_estatus)
        if f_ubicacion:
            from django.db.models import Q
            reportes_qs = reportes_qs.filter(Q(colonia__icontains=f_ubicacion) | Q(localidad__icontains=f_ubicacion))
            
        contexto['reportes'] = reportes_qs.order_by('-fecha_reporte')
        contexto['personal_activo'] = PersonalAdministrativo.objects.filter(is_active=True)
        
        # Guardar valores de filtros en contexto
        contexto['f_prioridad'] = f_prioridad
        contexto['f_tipo'] = f_tipo
        contexto['f_estatus'] = f_estatus
        contexto['f_ubicacion'] = f_ubicacion
        
        # Estadísticas del panel de control (basadas en la consulta FILTRADA actual)
        contexto['stats_pendientes'] = reportes_qs.filter(estatus='PENDIENTE').count()
        contexto['stats_en_proceso'] = reportes_qs.filter(estatus='EN_PROCESO').count()
        contexto['stats_resueltos'] = reportes_qs.filter(estatus='RESUELTO').count()
        contexto['stats_total'] = reportes_qs.count()
        
        # Conteo agrupado por tipo de servicio en la lista filtrada
        from django.db.models import Count
        tipos_counts = reportes_qs.values('tipo_servicio').annotate(count=Count('id'))
        tipos_dict = {t[0]: 0 for t in ReporteRiesgo.SERVICIO_CHOICES}
        for tc in tipos_counts:
            tipos_dict[tc['tipo_servicio']] = tc['count']
        contexto['tipos_filtrados_counts'] = tipos_dict
    # Cargar datos para la sección de analíticas de sucesos
    if seccion == 'analiticas':
        try:
            from portal.views.analiticas import obtener_datos_analiticas
            obtener_datos_analiticas(request, contexto)
        except Exception as e:
            # Tolerancia a fallos: aislar errores del módulo analítico
            contexto['analiticas_error'] = True
            import logging
            logging.error(f"[FaultIsolation] Error en el módulo de analíticas: {str(e)}")

    # Cargar datos adicionales según la sección elegida (Solo SUPER)
    if personal.rol_nivel == 'SUPER':
        if seccion == 'personal':
            contexto['solicitudes_pendientes'] = PersonalAdministrativo.objects.filter(is_active=False)
            contexto['personal_activo'] = PersonalAdministrativo.objects.filter(is_active=True).exclude(id=personal.id)
        elif seccion == 'tramites':
            contexto['tramites'] = Tramite.objects.all()

    if seccion == 'trabajadores':
        contexto['todos_trabajadores'] = Trabajador.objects.all().order_by('nombre')
        contexto['trabajadores_bomberos'] = Trabajador.objects.filter(categoria='BOMBERO').order_by('nombre')
        contexto['trabajadores_ambulancias'] = Trabajador.objects.filter(categoria='AMBULANCIA').order_by('nombre')
        contexto['trabajadores_policias'] = Trabajador.objects.filter(categoria='POLICIA').order_by('nombre')
        contexto['trabajadores_turno1'] = Trabajador.objects.filter(turno='TURNO_1').order_by('nombre')
        contexto['trabajadores_turno2'] = Trabajador.objects.filter(turno='TURNO_2').order_by('nombre')
        contexto['trabajadores_turno1_count'] = contexto['trabajadores_turno1'].count()
        contexto['trabajadores_turno2_count'] = contexto['trabajadores_turno2'].count()

        # Plantillas de Guardia (24 Hours) y Calendario Programado
        contexto['plantillas_guardia'] = PlantillaGuardia.objects.all().prefetch_related('trabajadores').order_by('nombre')
        
        hoy = datetime.date.today()
        contexto['hoy_fecha'] = hoy
        contexto['guardia_hoy'] = ProgramacionGuardia.objects.filter(fecha=hoy).select_related('plantilla').prefetch_related('plantilla__trabajadores').first()

        # Programaciones del mes actual para el calendario
        programaciones_mes = ProgramacionGuardia.objects.filter(
            fecha__year=hoy.year,
            fecha__month=hoy.month
        ).select_related('plantilla').prefetch_related('plantilla__trabajadores')
        contexto['programaciones_mes'] = programaciones_mes

# Alertas críticas generales para banner/sirena sonora
    contexto['criticas_pendientes'] = ReporteRiesgo.objects.filter(prioridad='ALTA', estatus='PENDIENTE').order_by('-fecha_reporte')
    contexto['total_criticas_pendientes'] = contexto['criticas_pendientes'].count()
            
    return render(request, 'portal/dashboard.html', contexto)

# Acciones de Asignación y Control de Emergencias (SUPER / VALIDADOR / CAPTURISTA)

# Agregar Entrada de Sucesos en la Bitácora

# Acciones de Validación de Solicitudes (Solo SUPER y VALIDADOR)
@login_required(login_url='login_unificado')
def aprobar_solicitud(request, solicitud_id):
    personal = request.user
    if personal.rol_nivel not in ['SUPER', 'VALIDADOR']:
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard_admin')
        
    solicitud = get_object_or_404(SolicitudTramite, id=solicitud_id)
    solicitud.estatus = 'APROBADO'
    solicitud.save()
    messages.success(request, f"La solicitud de '{solicitud.establecimiento}' para el trámite '{solicitud.tramite.titulo}' ha sido aprobada.")
    return redirect('dashboard_admin')

@login_required(login_url='login_unificado')
def buscar_solicitud(request):
    pass

@login_required(login_url='login_unificado')
def rechazar_solicitud(request, solicitud_id):
    personal = request.user
    if personal.rol_nivel not in ['SUPER', 'VALIDADOR']:
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard_admin')
        
    solicitud = get_object_or_404(SolicitudTramite, id=solicitud_id)
    solicitud.estatus = 'RECHAZADO'
    solicitud.save()
    messages.success(request, f"La solicitud de '{solicitud.establecimiento}' ha sido rechazada.")
    return redirect('dashboard_admin')

# Escapar caracteres reservados de LaTeX para evitar fallos de compilación
def escapar_latex(texto):
    if not texto:
        return ""
    texto = str(texto)
    # Mapeo de caracteres reservados de LaTeX
    caracteres = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in caracteres.items():
        texto = texto.replace(char, replacement)
    return texto

# Vista para generar y descargar la plantilla de Solicitud en LaTeX (.tex)
@login_required(login_url='login_unificado')
def descargar_solicitud_latex(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudTramite, id=solicitud_id)
    
    # Decodificar el mes a español para el formato LaTeX
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    dia = str(solicitud.creado_en.day)
    mes = meses.get(solicitud.creado_en.month, 'Enero')
    anio = str(solicitud.creado_en.year)
    anio_digito = anio[-1] if len(anio) > 0 else '6'
    
    # Escapar campos de texto para LaTeX
    establecimiento = escapar_latex(solicitud.establecimiento)
    propietario = escapar_latex(solicitud.propietario_representante)
    giro = escapar_latex(solicitud.giro)
    domicilio = escapar_latex(solicitud.domicilio_calle)
    no_ext = escapar_latex(solicitud.no_ext)
    no_int = escapar_latex(solicitud.no_int)
    entre = escapar_latex(solicitud.entre_calles)
    colonia = escapar_latex(solicitud.colonia)
    tel_contacto = escapar_latex(solicitud.telefono_contacto)
    horario = escapar_latex(solicitud.horario_funcionamiento)
    correo_c = escapar_latex(solicitud.correo_contacto)
    
    # Checks de documentos comunes
    doc_ine = "X" if solicitud.doc_ine else " "
    doc_croquis = "X" if solicitud.doc_croquis else " "
    doc_fotos = "X" if solicitud.doc_fotos else " "
    doc_predial = "X" if solicitud.doc_predial else " "

    # CASO 1: ANUNCIOS Y ANTENAS
    if solicitud.tramite.form_type == 'ANUNCIOS_PC':
        inspeccion_atiende = escapar_latex(solicitud.inspeccion_atiende)
        
        op1 = "X" if solicitud.tipo_anuencia_anuncio == 'ANUNCIO' else " "
        op2 = "X" if solicitud.tipo_anuencia_anuncio == 'ANTENA' else " "
        op3 = "X" if solicitud.tipo_anuencia_anuncio == 'RENOVACION_ANUNCIO' else " "
        
        # Checks de requisitos específicos
        req_estructural = "X" if solicitud.req_estructural else " "
        req_responsiva = "X" if solicitud.req_responsiva_estabilidad else " "
        req_bitacora = "X" if solicitud.req_bitacora_anuncio else " "
        req_seguro = "X" if solicitud.req_seguro else " "
        req_vecinos = "X" if solicitud.req_anuencia_vecinos else " "
        req_riesgo = "X" if solicitud.req_analisis_riesgo else " "
        req_pago = "X" if solicitud.req_pago else " "
        
        latex_template = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage[margin=1.5cm]{geometry}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{amssymb}
\usepackage{array}
\usepackage{fancyhdr}

% Configuración de encabezado y pie de página
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\small\itshape Dirección: Calz San Ramón S/N Col. Fracc. Arboleda San Ramón, Ver. C.P. 94274 / Teléfono: (229) 955 4000}

\begin{document}

% Encabezado con logos institucionales
\begin{center}
    \begin{tabularx}{\textwidth}{X c X}
        \noindent\makebox[0pt][l]{\includegraphics[height=1.8cm]{logo_medellin}} & 
        \centering\includegraphics[height=1.2cm]{logo_pc} & 
        \raggedleft\noindent\makebox[0pt][r]{\includegraphics[height=1.8cm]{escudo}}
    \end{tabularx}
    
    \vspace{0.3cm}
    {\bfseries\large UNIDAD MUNICIPAL DE PROTECCIÓN CIVIL Y BOMBEROS} \\
    \vspace{0.05cm}
    {\bfseries\large H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VER.} \\
    \vspace{0.05cm}
    {\bfseries\large 2026-2029}
\end{center}

\vspace{0.4cm}

\begin{flushright}
    Medellín de Bravo, Ver. A \underbar{ <<dia>> } de \underbar{ <<mes>> } del 202\underbar{ <<anio_digito>> }
\end{flushright}

\vspace{0.5cm}

\noindent {\bfseries LPC. ANTONIO ROSAS DELON} \\
{\bfseries DIRECTOR MUNICIPAL DE PROTECCIÓN CIVIL} \\
{\bfseries DE MEDELLÍN DE BRAVO, VER.} \\
{\bfseries PRESENTE:}

\vspace{0.4cm}

\noindent Por medio de la presente solicito a usted el trámite indicado, con el fin de obtener el dictamen y/o anuencia de Protección civil, una vez cubiertos en su totalidad los requerimientos de seguridad y haber realizado los pagos correspondientes.

\vspace{0.4cm}

\noindent Marque con una \textbf{X} los trámites solicitados:

\vspace{0.2cm}
\noindent
\begin{tabularx}{\textwidth}{|c|X|}
    \hline
    \makebox[0.5cm][c]{<<op1>>} & Anuencia de anuncio de Protección Civil \\ \hline
    \makebox[0.5cm][c]{<<op2>>} & Anuencia de antena de Protección Civil \\ \hline
    \makebox[0.5cm][c]{<<op3>>} & Renovación de anuencia de anuncio de Protección Civil \\ \hline
\end{tabularx}

\vspace{0.5cm}
\begin{center}
    {\bfseries\large Datos Local Comercial:}
\end{center}
\vspace{0.2cm}

\noindent Nombre de propietario, representante legal, y/o nombre de quien saldrá el documento: \\
\underbar{ \makebox[\textwidth][l]{<<propietario>>} }

\vspace{0.3cm}
\noindent Nombre de quien atenderá la inspección: \underbar{ \makebox[13cm][l]{<<inspeccion_atiende>>} }

\vspace{0.3cm}
\noindent Razón Social: \underbar{ \makebox[14cm][l]{<<establecimiento>>} }

\vspace{0.3cm}
\noindent Giro: \underbar{ \makebox[16cm][l]{<<giro>>} }

\vspace{0.3cm}
\noindent Domicilio de la inspección: \underbar{ \makebox[8cm][l]{<<domicilio>>} } No. Ext: \underbar{ \makebox[2cm][l]{<<no_ext>>} } No. Int: \underbar{ \makebox[2cm][l]{<<no_int>>} }

\vspace{0.3cm}
\noindent Entre: \underbar{ \makebox[8cm][l]{<<entre>>} } COL. \underbar{ \makebox[5cm][l]{<<colonia>>} }

\vspace{0.3cm}
\noindent Teléfono: \underbar{ \makebox[7cm][l]{<<tel_contacto>>} } Horario: \underbar{ \makebox[7cm][l]{<<horario>>} }

\vspace{0.6cm}
\begin{center}
    {\bfseries\large DOCUMENTOS REQUERIDOS}
\end{center}
\begin{itemize}
    \item[a)] [ <<doc_ine>> ] Fotocopia de credencial de elector de quien realiza el trámite.
    \item[b)] [ <<doc_croquis>> ] Croquis de ubicación.
    \item[c)] [ <<doc_fotos>> ] Dos Fotografías impresas en papel y a color del terreno.
    \item[d)] [ <<doc_predial>> ] Contrato de arrendamiento o pago de predial.
\end{itemize}

\vspace{0.4cm}
\begin{center}
    {\bfseries\large PARA EMISIÓN DE DICTAMEN O FACTIBILIDAD DE PROTECCIÓN CIVIL}
\end{center}
\begin{enumerate}
    \item[a)] ( <<req_estructural>> ) Dictamen Estructural.
    \item[b)] ( <<req_responsiva>> ) Responsiva de Estabilidad Y Seguridad Estructural.
    \item[c)] ( <<req_bitacora>> ) Programa de Mantenimiento y/o Bitácora de Mantenimiento del Anuncio.
    \item[d)] ( <<req_seguro>> ) Póliza De Responsabilidad Civil Vigente.
    \item[e)] ( <<req_vecinos>> ) Anuencia de vecinos.
    \item[f)] ( <<req_riesgo>> ) Análisis de riesgo por un tercero acreditado con registro municipal (según aplique).
    \item[g)] ( <<req_pago>> ) Pago de derechos de servicios prestado en materia de protección civil.
\end{enumerate}

\vspace{1.2cm}

\noindent Nombre y firma de quien realiza el trámite: \underbar{ \makebox[10cm][l]{<<propietario>>} }

\vspace{0.4cm}
\noindent Teléfono: \underbar{ \makebox[6cm][l]{<<tel_contacto>>} } Correo Electrónico: \underbar{ \makebox[7.3cm][l]{<<correo_c>>} }

\end{document}
"""
        latex_content = latex_template.replace("<<dia>>", dia)
        latex_content = latex_content.replace("<<mes>>", mes)
        latex_content = latex_content.replace("<<anio_digito>>", anio_digito)
        latex_content = latex_content.replace("<<op1>>", op1)
        latex_content = latex_content.replace("<<op2>>", op2)
        latex_content = latex_content.replace("<<op3>>", op3)
        latex_content = latex_content.replace("<<propietario>>", propietario)
        latex_content = latex_content.replace("<<inspeccion_atiende>>", inspeccion_atiende)
        latex_content = latex_content.replace("<<establecimiento>>", establecimiento)
        latex_content = latex_content.replace("<<giro>>", giro)
        latex_content = latex_content.replace("<<domicilio>>", domicilio)
        latex_content = latex_content.replace("<<no_ext>>", no_ext)
        latex_content = latex_content.replace("<<no_int>>", no_int)
        latex_content = latex_content.replace("<<entre>>", entre)
        latex_content = latex_content.replace("<<colonia>>", colonia)
        latex_content = latex_content.replace("<<tel_contacto>>", tel_contacto)
        latex_content = latex_content.replace("<<horario>>", horario)
        latex_content = latex_content.replace("<<doc_ine>>", doc_ine)
        latex_content = latex_content.replace("<<doc_croquis>>", doc_croquis)
        latex_content = latex_content.replace("<<doc_fotos>>", doc_fotos)
        latex_content = latex_content.replace("<<doc_predial>>", doc_predial)
        latex_content = latex_content.replace("<<req_estructural>>", req_estructural)
        latex_content = latex_content.replace("<<req_responsiva>>", req_responsiva)
        latex_content = latex_content.replace("<<req_bitacora>>", req_bitacora)
        latex_content = latex_content.replace("<<req_seguro>>", req_seguro)
        latex_content = latex_content.replace("<<req_vecinos>>", req_vecinos)
        latex_content = latex_content.replace("<<req_riesgo>>", req_riesgo)
        latex_content = latex_content.replace("<<req_pago>>", req_pago)
        latex_content = latex_content.replace("<<correo_c>>", correo_c)

    # CASO 3: CONSTRUCCIÓN, REMODELACIÓN Y DEMOLICIÓN (FORMATO 3)
    elif solicitud.tramite.form_type == 'CONSTRUCCION_PC':
        superficie_terreno = escapar_latex(solicitud.superficie_terreno or "")
        superficie_construccion = escapar_latex(solicitud.superficie_construccion or "")
        realiza_nombre = escapar_latex(solicitud.realiza_nombre or "")
        realiza_telefono = escapar_latex(solicitud.realiza_telefono or "")
        
        op1 = "X" if solicitud.tipo_anuencia_construccion == 'CONSTRUCCION' else " "
        op2 = "X" if solicitud.tipo_anuencia_construccion == 'REMODELACION' else " "
        op3 = "X" if solicitud.tipo_anuencia_construccion == 'DEMOLICION' else " "

        doc_ine = "X" if solicitud.doc_ine else " "
        doc_predial = "X" if solicitud.doc_predial else " "
        doc_croquis = "X" if solicitud.doc_croquis else " "
        doc_titulo_propiedad = "X" if solicitud.doc_titulo_propiedad else " "
        
        req_plano_arquitectonico = "X" if solicitud.req_plano_arquitectonico else " "
        req_constancia_no_afectacion = "X" if solicitud.req_constancia_no_afectacion else " "
        req_uso_suelo = "X" if solicitud.req_uso_suelo else " "
        req_analisis_riesgo = "X" if solicitud.req_analisis_riesgo else " "
        doc_fotos = "X" if solicitud.doc_fotos else " "
        req_pago = "X" if solicitud.req_pago else " "

        latex_template = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage[margin=1.5cm]{geometry}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{amssymb}
\usepackage{array}
\usepackage{fancyhdr}

% Configuración de encabezado y pie de página
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\small\itshape Dirección: Calz San Ramón S/N Col. Fracc. Arboleda San Ramón, Ver. C.P. 94274 / Teléfono: (229) 955 4000}

\begin{document}

% Encabezado con logos institucionales
\begin{center}
    \begin{tabularx}{\textwidth}{X c X}
        \noindent\makebox[0pt][l]{\includegraphics[height=1.8cm]{logo_medellin}} & 
        \centering\includegraphics[height=1.2cm]{logo_pc} & 
        \raggedleft\noindent\makebox[0pt][r]{\includegraphics[height=1.8cm]{escudo}}
    \end{tabularx}
    
    \vspace{0.3cm}
    {\bfseries\large UNIDAD MUNICIPAL DE PROTECCIÓN CIVIL Y BOMBEROS} \\
    \vspace{0.05cm}
    {\bfseries\large H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VER.} \\
    \vspace{0.05cm}
    {\bfseries\large 2026-2029}
\end{center}

\vspace{0.4cm}

\begin{flushright}
    Medellín de Bravo, Ver. A \underbar{ <<dia>> } de \underbar{ <<mes>> } del 202\underbar{ <<anio_digito>> }
\end{flushright}

\vspace{0.5cm}

\noindent {\bfseries LPC. ANTONIO ROSAS DELON} \\
{\bfseries DIRECTOR MUNICIPAL DE PROTECCIÓN CIVIL} \\
{\bfseries DE MEDELLÍN DE BRAVO, VER.} \\
{\bfseries PRESENTE:}

\vspace{0.4cm}

\noindent Por medio de la presente solicito a usted el trámite indicado, con el fin de obtener el no inconveniente y/o dictamen de protección civil, una vez cubiertos en su totalidad los requerimientos de seguridad y haber realizado los pagos correspondientes.

\vspace{0.4cm}

\noindent Marque con una \textbf{X} los trámites solicitados:

\vspace{0.2cm}
\noindent
\begin{tabularx}{\textwidth}{|c|X|}
    \hline
    \makebox[0.5cm][c]{<<op1>>} & Revisión de planos, proyecto para No inconveniente de construcción \\ \hline
    \makebox[0.5cm][c]{<<op2>>} & Inspección de inmueble y revisión de planos para remodelación y ampliación \\ \hline
    \makebox[0.5cm][c]{<<op3>>} & Inspección de inmueble a demoler \\ \hline
\end{tabularx}

\vspace{0.4cm}
\begin{center}
    {\bfseries\large Datos del Inmueble:}
\end{center}
\vspace{0.2cm}

\noindent Nombre de propietario, representante legal, y/o de quien saldrá el documento: \\
\underbar{ \makebox[\textwidth][l]{<<propietario>>} }

\vspace{0.3cm}
\noindent Teléfono: \underbar{ \makebox[4cm][l]{<<tel_contacto>>} } \hfill Razón Social/Local: \underbar{ \makebox[9cm][l]{<<establecimiento>>} }

\vspace{0.3cm}
\noindent Giro: \underbar{ \makebox[7cm][l]{<<giro>>} } \hfill Domicilio: \underbar{ \makebox[7cm][l]{<<domicilio>>} }

\vspace{0.3cm}
\noindent No. Ext: \underbar{ \makebox[2cm][l]{<<no_ext>>} } \hfill No. Int: \underbar{ \makebox[2cm][l]{<<no_int>>} } \hfill Colonia: \underbar{ \makebox[6cm][l]{<<colonia>>} }

\vspace{0.3cm}
\noindent Superficie de Terreno: \underbar{ \makebox[4cm][l]{<<superficie_terreno>>} } \hfill Superficie de Construcción: \underbar{ \makebox[4cm][l]{<<superficie_construccion>>} }

\vspace{0.4cm}
\noindent {\bfseries 1. Documentos solicitados:}
\begin{itemize}
    \item[a)] [ <<doc_ine>> ] Fotocopia de credencial de elector de quien realiza el trámite.
    \item[b)] [ <<doc_predial>> ] Copia de pago de predial.
    \item[c)] [ <<doc_croquis>> ] Croquis de localización.
    \item[d)] [ <<doc_titulo_propiedad>> ] Copia certificada del título de propiedad inscrito en el RPP.
\end{itemize}

\noindent {\bfseries 2. Para Emisión de Dictamen:}
\begin{itemize}
    \item[a)] [ <<req_plano_arquitectonico>> ] Plano arquitectónico del proyecto de construcción 90 X 60 firmado por perito responsable de obra y/o Memoria Descriptiva del Proyecto.
    \item[b)] [ <<req_constancia_no_afectacion>> ] Constancia de no afectación (CFE, CONAGUA, PEMEX e INAH) entre otros.
    \item[c)] [ <<req_uso_suelo>> ] Constancia de Zonificación y/o permiso de uso de suelo emitida por la autoridad competente.
    \item[d)] [ <<req_analisis_riesgo>> ] Análisis de riesgo realizado por un tercer acreditado con registro municipal.
    \item[e)] [ <<doc_fotos>> ] Fotografías del predio.
    \item[f)] [ <<req_pago>> ] Pago de derechos de servicios prestados en materia de protección civil.
\end{itemize}

\vspace{0.8cm}
\begin{center}
    \begin{tabular}{c}
        \underbar{\makebox[7cm]{}} \\
        {\bfseries <<realiza_nombre>>} \\
        Nombre y firma de quien realiza el trámite \\
        Teléfono: <<realiza_telefono>>
    \end{tabular}
\end{center}

\end{document}
"""

        latex_content = latex_template
        latex_content = latex_content.replace("<<dia>>", dia)
        latex_content = latex_content.replace("<<mes>>", mes)
        latex_content = latex_content.replace("<<anio_digito>>", anio_digito)
        latex_content = latex_content.replace("<<op1>>", op1)
        latex_content = latex_content.replace("<<op2>>", op2)
        latex_content = latex_content.replace("<<op3>>", op3)
        latex_content = latex_content.replace("<<propietario>>", propietario)
        latex_content = latex_content.replace("<<tel_contacto>>", tel_contacto)
        latex_content = latex_content.replace("<<establecimiento>>", establecimiento)
        latex_content = latex_content.replace("<<giro>>", giro)
        latex_content = latex_content.replace("<<domicilio>>", domicilio)
        latex_content = latex_content.replace("<<no_ext>>", no_ext)
        latex_content = latex_content.replace("<<no_int>>", no_int)
        latex_content = latex_content.replace("<<colonia>>", colonia)
        latex_content = latex_content.replace("<<superficie_terreno>>", superficie_terreno)
        latex_content = latex_content.replace("<<superficie_construccion>>", superficie_construccion)
        latex_content = latex_content.replace("<<doc_ine>>", doc_ine)
        latex_content = latex_content.replace("<<doc_predial>>", doc_predial)
        latex_content = latex_content.replace("<<doc_croquis>>", doc_croquis)
        latex_content = latex_content.replace("<<doc_titulo_propiedad>>", doc_titulo_propiedad)
        latex_content = latex_content.replace("<<req_plano_arquitectonico>>", req_plano_arquitectonico)
        latex_content = latex_content.replace("<<req_constancia_no_afectacion>>", req_constancia_no_afectacion)
        latex_content = latex_content.replace("<<req_uso_suelo>>", req_uso_suelo)
        latex_content = latex_content.replace("<<req_analisis_riesgo>>", req_analisis_riesgo)
        latex_content = latex_content.replace("<<doc_fotos>>", doc_fotos)
        latex_content = latex_content.replace("<<req_pago>>", req_pago)
        latex_content = latex_content.replace("<<realiza_nombre>>", realiza_nombre)
        latex_content = latex_content.replace("<<realiza_telefono>>", realiza_telefono)

    # CASO 4: REGISTRO DE TERCEROS ACREDITADOS (FORMATO 4)
    elif solicitud.tramite.form_type == 'TERCEROS_PC':
        realiza_nombre = escapar_latex(solicitud.realiza_nombre or "")
        realiza_telefono = escapar_latex(solicitud.realiza_telefono or "")
        realiza_correo = escapar_latex(solicitud.realiza_correo or "")
        
        op1 = "X" if solicitud.tipo_anuencia_terceros == 'NUEVO_INGRESO' else " "
        op2 = "X" if solicitud.tipo_anuencia_terceros == 'RENOVACION_REGISTRO' else " "

        doc_ine = "X" if solicitud.doc_ine else " "
        req_cedula_estatal = "X" if solicitud.req_cedula_estatal else " "
        req_pago = "X" if solicitud.req_pago else " "
        
        if solicitud.tipo_anuencia_terceros == 'NUEVO_INGRESO':
            req_curriculum = "X" if solicitud.req_curriculum else " "
        else:
            req_curriculum = "-- No requerido --"

        latex_template = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage[margin=1.5cm]{geometry}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{amssymb}
\usepackage{array}
\usepackage{fancyhdr}

% Configuración de encabezado y pie de página
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\small\itshape Dirección: Calz San Ramón S/N Col. Fracc. Arboleda San Ramón, Ver. C.P. 94274 / Teléfono: (229) 955 4000}

\begin{document}

% Encabezado con logos institucionales
\begin{center}
    \begin{tabularx}{\textwidth}{X c X}
        \noindent\makebox[0pt][l]{\includegraphics[height=1.8cm]{logo_medellin}} & 
        \centering\includegraphics[height=1.2cm]{logo_pc} & 
        \raggedleft\noindent\makebox[0pt][r]{\includegraphics[height=1.8cm]{escudo}}
    \end{tabularx}
    
    \vspace{0.3cm}
    {\bfseries\large UNIDAD MUNICIPAL DE PROTECCIÓN CIVIL Y BOMBEROS} \\
    \vspace{0.05cm}
    {\bfseries\large H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VER.} \\
    \vspace{0.05cm}
    {\bfseries\large 2026-2029}
\end{center}

\vspace{0.4cm}

\begin{flushright}
    Medellín de Bravo, Ver. A \underbar{ <<dia>> } de \underbar{ <<mes>> } del 202\underbar{ <<anio_digito>> }
\end{flushright}

\vspace{0.5cm}

\noindent {\bfseries LPC. ANTONIO ROSAS DELON} \\
{\bfseries DIRECTOR MUNICIPAL DE PROTECCIÓN CIVIL} \\
{\bfseries DE MEDELLÍN DE BRAVO, VER.} \\
{\bfseries PRESENTE:}

\vspace{0.4cm}

\noindent Por medio de la presente solicito a usted el trámite indicado, con el fin de obtener el registro municipal de terceros acreditados y las empresas capacitadoras e instructores independientes en el padrón municipal de protección civil y realizar el pago de derecho correspondiente.

\vspace{0.4cm}

\noindent Marque con una \textbf{X} los trámites solicitados:

\vspace{0.2cm}
\noindent
\begin{tabularx}{\textwidth}{|c|X|}
    \hline
    \makebox[0.5cm][c]{<<op1>>} & REGISTRO DE TERCER ACREDITADO Y/O EMPRESAS CAPACITADORAS E INSTRUCTORES EN EL PADRÓN MUNICIPAL (NUEVO INGRESO) \\ \hline
    \makebox[0.5cm][c]{<<op2>>} & RENOVACIÓN DE REGISTRO EN EL PADRÓN MUNICIPAL \\ \hline
\end{tabularx}

\vspace{0.4cm}
\begin{center}
    {\bfseries\large Datos para el Registro:}
\end{center}
\vspace{0.2cm}

\noindent Nombre de la persona física, moral o Razón Social: \\
\underbar{ \makebox[\textwidth][l]{<<establecimiento>>} }

\vspace{0.3cm}
\noindent RFC: \underbar{ \makebox[4cm][l]{<<rfc>>} } \hfill Representante Legal: \underbar{ \makebox[8cm][l]{<<propietario>>} }

\vspace{0.3cm}
\noindent Teléfono de Contacto: \underbar{ \makebox[4cm][l]{<<tel_contacto>>} } \hfill Correo Electrónico: \underbar{ \makebox[8cm][l]{<<correo_contacto>>} }

\vspace{0.4cm}
\noindent {\bfseries 1. Documentos solicitados:}
\begin{itemize}
    \item[1)] [ <<doc_ine>> ] Copia de INE del Solicitante o Representante.
    \item[2)] [ <<req_cedula_estatal>> ] Cédula de Protección Civil Estatal (Alcances).
    \item[3)] [ <<req_pago>> ] Pago de Derechos correspondientes.
\end{itemize}

\noindent {\bfseries 2. Historial Profesional (Solo Nuevos Registros):}
\begin{itemize}
    \item[1)] [ <<req_curriculum>> ] Curriculum Vitae.
\end{itemize}

\vspace{0.8cm}
\begin{center}
    \begin{tabular}{c}
        \underbar{\makebox[7cm]{}} \\
        {\bfseries <<realiza_nombre>>} \\
        Nombre y firma de quien realiza el trámite \\
        Teléfono: <<realiza_telefono>>
    \end{tabular}
\end{center}

\end{document}
"""

        latex_content = latex_template
        latex_content = latex_content.replace("<<dia>>", dia)
        latex_content = latex_content.replace("<<mes>>", mes)
        latex_content = latex_content.replace("<<anio_digito>>", anio_digito)
        latex_content = latex_content.replace("<<op1>>", op1)
        latex_content = latex_content.replace("<<op2>>", op2)
        latex_content = latex_content.replace("<<establecimiento>>", establecimiento)
        latex_content = latex_content.replace("<<rfc>>", rfc)
        latex_content = latex_content.replace("<<propietario>>", propietario)
        latex_content = latex_content.replace("<<tel_contacto>>", tel_contacto)
        latex_content = latex_content.replace("<<correo_contacto>>", correo_c)
        latex_content = latex_content.replace("<<doc_ine>>", doc_ine)
        latex_content = latex_content.replace("<<req_cedula_estatal>>", req_cedula_estatal)
        latex_content = latex_content.replace("<<req_pago>>", req_pago)
        latex_content = latex_content.replace("<<req_curriculum>>", req_curriculum)
        latex_content = latex_content.replace("<<realiza_nombre>>", realiza_nombre)
        latex_content = latex_content.replace("<<realiza_telefono>>", realiza_telefono)

    # CASO 2: ANUENCIA COMERCIAL DE PROTECCIÓN CIVIL (FORMATO 1)
    else:
        ui_nombre = escapar_latex(solicitud.unidad_interna_nombre)
        ui_tel = escapar_latex(solicitud.unidad_interna_tel)
        capacidad = escapar_latex(solicitud.capacidad_fija)
        superficie = escapar_latex(solicitud.superficie_m2)

        op1 = "X" if solicitud.tipo_anuencia == 'OPERATIVA' else " "
        op2 = "X" if solicitud.tipo_anuencia == 'RENOVACION' else " "
        op3 = "X" if solicitud.tipo_anuencia == 'RECOMENDACIONES' else " "
        op4 = "X" if solicitud.tipo_anuencia == 'TEMPORAL' else " "
        
        req_programa = "X" if solicitud.req_programa else " "
        req_corresponsabilidad = "X" if solicitud.req_corresponsabilidad else " "
        req_capacitacion = "X" if solicitud.req_capacitacion else " "
        req_gas = "X" if solicitud.req_gas else " "
        req_electrico = "X" if solicitud.req_electrico else " "
        req_estructural = "X" if solicitud.req_estructural else " "
        req_seguro = "X" if solicitud.req_seguro else " "
        req_pago = "X" if solicitud.req_pago else " "
        
        latex_template = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage[margin=1.5cm]{geometry}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{amssymb}
\usepackage{array}
\usepackage{fancyhdr}

% Configuración de encabezado y pie de página
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\small\itshape Dirección: Calz San Ramón S/N Col. Fracc. Arboleda San Ramón, Ver. C.P. 94274 / Teléfono: (229) 955 4000}

\begin{document}

% Encabezado con logos institucionales
\begin{center}
    \begin{tabularx}{\textwidth}{X c X}
        \noindent\makebox[0pt][l]{\includegraphics[height=1.8cm]{logo_medellin}} & 
        \centering\includegraphics[height=1.2cm]{logo_pc} & 
        \raggedleft\noindent\makebox[0pt][r]{\includegraphics[height=1.8cm]{escudo}}
    \end{tabularx}
    
    \vspace{0.3cm}
    {\bfseries\large UNIDAD MUNICIPAL DE PROTECCIÓN CIVIL Y BOMBEROS} \\
    \vspace{0.05cm}
    {\bfseries\large H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VER.} \\
    \vspace{0.05cm}
    {\bfseries\large 2026-2029}
\end{center}

\vspace{0.4cm}

\begin{flushright}
    Medellín de Bravo, Ver. A \underbar{ <<dia>> } de \underbar{ <<mes>> } del 202\underbar{ <<anio_digito>> }
\end{flushright}

\vspace{0.5cm}

\noindent {\bfseries LPC. ANTONIO ROSAS DELON} \\
{\bfseries DIRECTOR MUNICIPAL DE PROTECCIÓN CIVIL} \\
{\bfseries DE MEDELLÍN DE BRAVO, VER.} \\
{\bfseries PRESENTE:}

\vspace{0.4cm}

\noindent Por medio de la presente solicito a usted el trámite indicado, con el fin de obtener la anuencia de protección civil, una vez cubiertos en su totalidad los requerimientos de seguridad y haber realizado los pagos correspondientes.

\vspace{0.4cm}

\noindent Marque con una \textbf{X} los trámites solicitados:

\vspace{0.2cm}
\noindent
\begin{tabularx}{\textwidth}{|c|X|}
    \hline
    \makebox[0.5cm][c]{<<op1>>} & Anuencia de operativa de protección civil a instalaciones públicas y privadas \\ \hline
    \makebox[0.5cm][c]{<<op2>>} & Renovación de anuencia operativa \\ \hline
    \makebox[0.5cm][c]{<<op3>>} & Pliego de Recomendaciones de eventos masivos \\ \hline
    \makebox[0.5cm][c]{<<op4>>} & Temporal (verificación de seguridad para puestos ambulantes) \\ \hline
\end{tabularx}

\vspace{0.5cm}
\begin{center}
    {\bfseries\large Datos Local Comercial:}
\end{center}
\vspace{0.2cm}

\noindent Nombre de propietario, representante legal, y/o nombre de quien saldrá el documento: \\
\underbar{ \makebox[\textwidth][l]{<<propietario>>} }

\vspace{0.3cm}
\noindent Nombre del titular o representante de la Unidad Interna: \underbar{ \makebox[8.5cm][l]{<<ui_nombre>>} } Tel: \underbar{ \makebox[3.5cm][l]{<<ui_tel>>} }

\vspace{0.3cm}
\noindent Razón Social: \underbar{ \makebox[9.5cm][l]{<<establecimiento>>} } Capacidad fija: \underbar{ \makebox[3cm][l]{<<capacidad>>} }

\vspace{0.3cm}
\noindent Giro: \\
\underbar{ \makebox[\textwidth][l]{<<giro>>} }

\vspace{0.3cm}
\noindent Domicilio: \underbar{ \makebox[8cm][l]{<<domicilio>>} } No. Ext: \underbar{ \makebox[2cm][l]{<<no_ext>>} } No. Int: \underbar{ \makebox[2cm][l]{<<no_int>>} }

\vspace{0.3cm}
\noindent Entre: \underbar{ \makebox[5cm][l]{<<entre>>} } COL. \underbar{ \makebox[4cm][l]{<<colonia>>} } Teléfono: \underbar{ \makebox[3.5cm][l]{<<tel_contacto>>} }

\vspace{0.3cm}
\noindent Horario: \underbar{ \makebox[4.5cm][l]{<<horario>>} } Metros cuadrados de superficie: \underbar{ \makebox[6.5cm][l]{<<superficie>>} }

\vspace{0.6cm}
\begin{center}
    {\bfseries\large DOCUMENTOS SOLICITADOS}
\end{center}
\begin{itemize}
    \item[a)] [ <<doc_ine>> ] Fotocopia de credencial de elector de quien realiza el trámite.
    \item[b)] [ <<doc_croquis>> ] Croquis de ubicación del Inmueble.
    \item[c)] [ <<doc_fotos>> ] Dos Fotografías impresas en papel a color de la fachada.
    \item[d)] [ <<doc_predial>> ] Copia del pago del predial o contrato de arrendamiento.
\end{itemize}

\vspace{0.4cm}
\begin{center}
    {\bfseries\large DOCUMENTOS PARA EMISIÓN DE ANUENCIA}
\end{center}
\begin{enumerate}
    \item[\textbf{1.}] ( <<req_programa>> ) Programa de protección civil en documento o CD formato PDF
    \item[\textbf{2.}] ( <<req_corresponsabilidad>> ) Carta de corresponsabilidad en papel seguridad de tercero acreditado.
    \item[\textbf{3.}] ( <<req_capacitacion>> ) Constancias de capacitación en uso y manejo de extintores y primeros auxilios.
    \item[\textbf{4.}] ( <<req_gas>> ) Dictamen de gas vigente emitido por unidad verificadora vigente NOM-004 y 013 SEDG
    \item[\textbf{5.}] ( <<req_electrico>> ) Dictamen eléctrico vigente NOM-001-SEDE-2012
    \item[\textbf{6.}] ( <<req_estructural>> ) Dictamen estructural vigente.
    \item[\textbf{7.}] ( <<req_seguro>> ) Póliza de seguro vigente.
    \item[\textbf{8.}] ( <<req_pago>> ) Pago correspondiente a la anuencia en trámite.
\end{enumerate}

\vspace{1.2cm}

\noindent Nombre y firma de quien realiza el trámite: \underbar{ \makebox[10cm][l]{<<propietario>>} }

\vspace{0.4cm}
\noindent Teléfono: \underbar{ \makebox[6cm][l]{<<tel_contacto>>} } Correo Electrónico: \underbar{ \makebox[7.3cm][l]{<<correo_c>>} }

\end{document}
"""
        latex_content = latex_template.replace("<<dia>>", dia)
        latex_content = latex_content.replace("<<mes>>", mes)
        latex_content = latex_content.replace("<<anio_digito>>", anio_digito)
        latex_content = latex_content.replace("<<op1>>", op1)
        latex_content = latex_content.replace("<<op2>>", op2)
        latex_content = latex_content.replace("<<op3>>", op3)
        latex_content = latex_content.replace("<<op4>>", op4)
        latex_content = latex_content.replace("<<propietario>>", propietario)
        latex_content = latex_content.replace("<<ui_nombre>>", ui_nombre)
        latex_content = latex_content.replace("<<ui_tel>>", ui_tel)
        latex_content = latex_content.replace("<<establecimiento>>", establecimiento)
        latex_content = latex_content.replace("<<capacidad>>", capacidad)
        latex_content = latex_content.replace("<<giro>>", giro)
        latex_content = latex_content.replace("<<domicilio>>", domicilio)
        latex_content = latex_content.replace("<<no_ext>>", no_ext)
        latex_content = latex_content.replace("<<no_int>>", no_int)
        latex_content = latex_content.replace("<<entre>>", entre)
        latex_content = latex_content.replace("<<colonia>>", colonia)
        latex_content = latex_content.replace("<<tel_contacto>>", tel_contacto)
        latex_content = latex_content.replace("<<horario>>", horario)
        latex_content = latex_content.replace("<<superficie>>", superficie)
        latex_content = latex_content.replace("<<doc_ine>>", doc_ine)
        latex_content = latex_content.replace("<<doc_croquis>>", doc_croquis)
        latex_content = latex_content.replace("<<doc_fotos>>", doc_fotos)
        latex_content = latex_content.replace("<<doc_predial>>", doc_predial)
        latex_content = latex_content.replace("<<req_programa>>", req_programa)
        latex_content = latex_content.replace("<<req_corresponsabilidad>>", req_corresponsabilidad)
        latex_content = latex_content.replace("<<req_capacitacion>>", req_capacitacion)
        latex_content = latex_content.replace("<<req_gas>>", req_gas)
        latex_content = latex_content.replace("<<req_electrico>>", req_electrico)
        latex_content = latex_content.replace("<<req_estructural>>", req_estructural)
        latex_content = latex_content.replace("<<req_seguro>>", req_seguro)
        latex_content = latex_content.replace("<<req_pago>>", req_pago)
        latex_content = latex_content.replace("<<correo_c>>", correo_c)
        
    # Servir el archivo .tex dinámicamente como descarga
    response = HttpResponse(latex_content, content_type='text/x-tex')
    response['Content-Disposition'] = f'attachment; filename="solicitud_{solicitud.establecimiento.replace(" ", "_")}.tex"'
    return response

# Vista para visualizar e imprimir el Oficio Membretado Oficial (Ctrl+P)
@login_required(login_url='login_unificado')
def imprimir_solicitud_oficio(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudTramite, id=solicitud_id)
    if solicitud.tramite.form_type == 'ANUNCIOS_PC':
        return render(request, 'portal/imprimir_solicitud_anuncio.html', {'solicitud': solicitud})
    elif solicitud.tramite.form_type == 'CONSTRUCCION_PC':
        return render(request, 'portal/imprimir_solicitud_construccion.html', {'solicitud': solicitud})
    elif solicitud.tramite.form_type == 'TERCEROS_PC':
        return render(request, 'portal/imprimir_solicitud_terceros.html', {'solicitud': solicitud})
    return render(request, 'portal/imprimir_solicitud.html', {'solicitud': solicitud})

# Acciones del SuperAdmin (Aprobación de Personal)



# Acciones de Trámites obsoletas removidas. Gestión directa en Django Admin.



def enviar_mensaje_chat(request):
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        solicitud_id = request.POST.get('solicitud_id')
        reporte_id = request.POST.get('reporte_id')
        
        if not mensaje or not mensaje.strip():
            messages.error(request, "El mensaje no puede estar vacío.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
            
        solicitud = None
        if solicitud_id and solicitud_id.isdigit():
            solicitud = get_object_or_404(SolicitudTramite, id=solicitud_id)
            
        reporte = None
        if reporte_id and reporte_id.isdigit():
            reporte = get_object_or_404(ReporteRiesgo, id=reporte_id)
            
        # Determinar remitente
        remitente_c = None
        remitente_a = None
        
        if request.user.is_authenticated:
            remitente_a = request.user
        else:
            curp_sesion = request.session.get('ciudadano_curp')
            if curp_sesion:
                remitente_c = Ciudadano.objects.filter(curp=curp_sesion).first()
                
        if not remitente_c and not remitente_a:
            if reporte:
                # Permitir comentarios públicos vinculándolos al ciudadano del reporte si existe
                remitente_c = reporte.ciudadano
            else:
                messages.error(request, "No autorizado para enviar mensajes.")
                return redirect('login_unificado')
            
        MensajeChat.objects.create(
            solicitud=solicitud,
            reporte=reporte,
            remitente_ciudadano=remitente_c,
            remitente_admin=remitente_a,
            mensaje=mensaje.strip()
        )
        messages.success(request, "Mensaje enviado.")
        
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required(login_url='login_unificado')
def crear_trabajador(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        categoria = request.POST.get('categoria', '').strip()
        turno = request.POST.get('turno', 'TURNO_1').strip()
        
        if nombre and telefono and categoria:
            Trabajador.objects.create(
                nombre=nombre,
                telefono=telefono,
                categoria=categoria,
                turno=turno
            )
            messages.success(request, f"Trabajador '{nombre}' registrado exitosamente.")
        else:
            messages.error(request, "Todos los campos son obligatorios para registrar un trabajador.")
            
    return redirect('/panel/?seccion=trabajadores')


@login_required(login_url='login_unificado')
def eliminar_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    nombre = trabajador.nombre
    trabajador.delete()
    messages.success(request, f"Trabajador '{nombre}' de la categoría '{trabajador.get_categoria_display()}' eliminado correctamente.")
    return redirect('/panel/?seccion=trabajadores')


@login_required(login_url='login_unificado')
def asignar_turno(request, trabajador_id, turno):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    if turno in ['TURNO_1', 'TURNO_2']:
        trabajador.turno = turno
        trabajador.save()
        messages.success(request, f"Se asignó a '{trabajador.nombre}' al {trabajador.get_turno_display()}.")
    else:
        messages.error(request, "El turno seleccionado no es válido.")
    return redirect('/panel/?seccion=trabajadores')
