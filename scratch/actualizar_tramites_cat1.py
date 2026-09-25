import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import Tramite

actualizaciones = {
    3: {
        'titulo': 'Anuencia Operativa de Protección Civil a Instalaciones Públicas y Privadas',
        'descripcion': 'Documento oficial emitido por la Dirección de Protección Civil que autoriza a un establecimiento comercial, industrial o de servicios el debido funcionamiento con base en las medidas y condiciones de seguridad humana, extintores y prevención de riesgos.',
        'requisitos': '1. Identificación oficial vigente del propietario o representante (INE / Pasaporte / Cédula); 2. Croquis de ubicación del inmueble con calles colindantes y referencias; 3. Fotografías a color de la fachada del establecimiento; 4. Boleta de pago del impuesto predial del año en curso o contrato de arrendamiento vigente; 5. Documentación técnica complementaria (Programa Interno y dictámenes de gas/luz según determine PC con base en el grado de riesgo).'
    },
    6: {
        'titulo': 'Pliego de Recomendaciones de Eventos Masivos',
        'descripcion': 'Evaluación técnica de las condiciones de seguridad y emisión del pliego de recomendaciones preventivas obligatorias para la realización de eventos públicos, privados, espectáculos, rodeos, bailes o concentraciones masivas en el municipio de Medellín de Bravo.',
        'requisitos': '1. Identificación oficial vigente del organizador o promotor responsable (INE); 2. Croquis y plano de distribución del evento (escenarios, rutas de evacuación, extintores y salidas); 3. Fotografías del recinto, predio o salón donde se llevará a cabo; 4. Programa Especial de Protección Civil y Plan de Evacuación; 5. Póliza de seguro de responsabilidad civil a terceros vigente para el evento; 6. Contrato de servicio médico con ambulancia prehospitalaria y paramédicos; 7. Permiso previo de Comercio y Gobernación Municipal.'
    },
    9: {
        'titulo': 'Renovación de Anuencia Operativa de Protección Civil',
        'descripcion': 'Refrendo y renovación anual de la Anuencia Operativa de Protección Civil para aquellos establecimientos comerciales o de servicios que ya cuentan con registro previo y mantienen activas sus medidas de prevención y seguridad.',
        'requisitos': '1. Identificación oficial vigente del titular o representante (INE); 2. Copia de la anuencia operativa del año anterior emitida por PC Medellín (o número de folio); 3. Boleta de pago del impuesto predial del año en curso o contrato vigente; 4. Fotografías actuales de la fachada y del extintor mostrando la etiqueta de recarga vigente; 5. Constancia de actualización de capacitación de brigadas internas; 6. Manifestación bajo protesta de no haber realizado modificaciones estructurales ni cambio de giro.'
    },
    12: {
        'titulo': 'Verificación de Seguridad para Puestos Ambulantes (Temporal)',
        'descripcion': 'Verificación física y expedición de anuencia temporal de medidas básicas de seguridad en materia de Protección Civil para puestos semifijos, comerciantes ambulantes o instalaciones temporales en vía pública, tianguis y festividades del municipio.',
        'requisitos': '1. Identificación oficial vigente del comerciante (INE); 2. Croquis de ubicación exacta del puesto en la vía pública o tianguis con referencias; 3. Permiso o cédula expedida por la Dirección de Comercio Municipal; 4. Fotografía del puesto mostrando extintor de polvo químico seco (PQS mín. 4.5 kg) vigente; 5. En caso de gas LP: manguera de alta presión con regulador y abrazaderas metálicas; 6. En caso de conexión eléctrica: cable de uso rudo continuo en una sola pieza.'
    }
}

for t_id, data in actualizaciones.items():
    tramite = Tramite.objects.filter(id=t_id).first()
    if tramite:
        tramite.titulo = data['titulo']
        tramite.descripcion = data['descripcion']
        tramite.requisitos = data['requisitos']
        tramite.save()
        print(f"[OK] Tramite ID {t_id} ({tramite.sub_tipo}) actualizado con exito.")
    else:
        print(f"[AVISO] Tramite ID {t_id} no encontrado.")

print("[FINALIZADO] Proceso de actualizacion de tramites Categoria 1 finalizado.")
