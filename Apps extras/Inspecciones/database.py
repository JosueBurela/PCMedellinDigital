import sqlite3
import os
from datetime import datetime, timedelta

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inspecciones.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de Configuración General
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracion (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    
    # Tabla de Órdenes de Inspección (Encabezado)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspecciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_corta TEXT NOT NULL, -- YYYY-MM-DD
        fecha_texto TEXT NOT NULL, -- Ej: JUEVES 06/AGOSTO/26
        horario TEXT NOT NULL,     -- Ej: De 10am A 2pm
        rutas_resumen TEXT NOT NULL,
        inspector TEXT NOT NULL,
        operador TEXT NOT NULL,
        director TEXT NOT NULL,
        estado TEXT DEFAULT 'Pendiente', -- Pendiente, En Proceso, Completado
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tabla de Ítems / Establecimientos a inspeccionar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspeccion_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspeccion_id INTEGER NOT NULL,
        numero INTEGER NOT NULL,
        ruta TEXT NOT NULL,
        establecimiento TEXT NOT NULL,
        mes_pago TEXT NOT NULL,
        realizado TEXT DEFAULT '',
        pendiente TEXT DEFAULT '',
        FOREIGN KEY (inspeccion_id) REFERENCES inspecciones (id) ON DELETE CASCADE
    )
    """)
    
    # Tabla de Catálogos (Rutas, Establecimientos, Personal)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS catalogos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT NOT NULL, -- 'ruta', 'establecimiento', 'inspector', 'operador'
        nombre TEXT NOT NULL,
        extra TEXT DEFAULT ''
    )
    """)
    
    # Valores por defecto para Configuración si no existen
    defaults = {
        "director_nombre": "L.E.D. DANIEL EDUARDO ROMERO PILAR",
        "director_cargo": "DIRECTOR MUNICIPAL DE LA UNIDAD DE\nPROTECCION CIVIL DE MEDELLIN DE BRAVO, VER.",
        "municipio": "MEDELLIN DE BRAVO, VER.",
        "horario_default": "De 10am A 2pm",
        "header_title": "DIRECCIÓN MUNICIPAL DE PROTECCIÓN CIVIL"
    }
    
    for key, val in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO configuracion (key, value) VALUES (?, ?)", (key, val))
        
    conn.commit()
    conn.close()
    
    # Insertar datos de muestra si la base de datos está recién creada
    seed_initial_data()

def get_config():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM configuracion")
    rows = cursor.fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}

def set_config(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO configuracion (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def guardar_inspeccion(fecha_corta, fecha_texto, horario, rutas_resumen, inspector, operador, items):
    config = get_config()
    director = config.get("director_nombre", "L.E.D. DANIEL EDUARDO ROMERO PILAR")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO inspecciones (fecha_corta, fecha_texto, horario, rutas_resumen, inspector, operador, director)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fecha_corta, fecha_texto, horario, rutas_resumen, inspector, operador, director))
    
    inspeccion_id = cursor.lastrowid
    
    for i, item in enumerate(items, start=1):
        cursor.execute("""
            INSERT INTO inspeccion_items (inspeccion_id, numero, ruta, establecimiento, mes_pago, realizado, pendiente)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (inspeccion_id, i, item.get("ruta", ""), item.get("establecimiento", ""), item.get("mes_pago", ""), item.get("realizado", ""), item.get("pendiente", "")))
        
    conn.commit()
    conn.close()
    return inspeccion_id

def actualizar_item_status(item_id, realizado, pendiente):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE inspeccion_items SET realizado = ?, pendiente = ? WHERE id = ?", (realizado, pendiente, item_id))
    conn.commit()
    conn.close()

def obtener_inspeccion(inspeccion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inspecciones WHERE id = ?", (inspeccion_id,))
    orden = cursor.fetchone()
    if not orden:
        conn.close()
        return None
        
    cursor.execute("SELECT * FROM inspeccion_items WHERE inspeccion_id = ? ORDER BY numero ASC", (inspeccion_id,))
    items = cursor.fetchall()
    conn.close()
    
    return {
        "orden": dict(orden),
        "items": [dict(it) for it in items]
    }

def eliminar_inspeccion(inspeccion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inspeccion_items WHERE inspeccion_id = ?", (inspeccion_id,))
    cursor.execute("DELETE FROM inspecciones WHERE id = ?", (inspeccion_id,))
    conn.commit()
    conn.close()

def listar_inspecciones_por_filtro(tipo_filtro, fecha_inicio=None, fecha_fin=None):
    """
    Filtros posibles:
    - 'todas': Todas las órdenes
    - 'hoy': Fecha del día actual
    - 'semana': Última semana
    - 'mes': Mes actual
    - 'bimestre': Últimos 2 meses
    - 'rango': Desde fecha_inicio a fecha_fin (YYYY-MM-DD)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")
    
    query = "SELECT * FROM inspecciones"
    params = []
    
    if tipo_filtro == 'hoy':
        query += " WHERE fecha_corta = ?"
        params.append(today_str)
    elif tipo_filtro == 'semana':
        inicio_semana = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        fin_semana = (today + timedelta(days=6 - today.weekday())).strftime("%Y-%m-%d")
        query += " WHERE fecha_corta BETWEEN ? AND ?"
        params.extend([inicio_semana, fin_semana])
    elif tipo_filtro == 'mes':
        inicio_mes = today.replace(day=1).strftime("%Y-%m-%d")
        query += " WHERE fecha_corta >= ?"
        params.append(inicio_mes)
    elif tipo_filtro == 'bimestre':
        inicio_bimestre = (today - timedelta(days=60)).strftime("%Y-%m-%d")
        query += " WHERE fecha_corta >= ?"
        params.append(inicio_bimestre)
    elif tipo_filtro == 'rango' and fecha_inicio and fecha_fin:
        query += " WHERE fecha_corta BETWEEN ? AND ?"
        params.extend([fecha_inicio, fecha_fin])
        
    query += " ORDER BY fecha_corta DESC, id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    resultados = []
    for r in rows:
        d = dict(r)
        d_full = obtener_inspeccion(d['id'])
        resultados.append(d_full)
    return resultados

def seed_initial_data():
    """Carga los datos iniciales de la hoja de ejemplo si no existen inspecciones."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM inspecciones")
    count = cursor.fetchone()["count"]
    conn.close()
    
    if count == 0:
        # Datos del ejemplo recibido en la fotografía
        items_ejemplo = [
            {"ruta": "TEJAR", "establecimiento": "GASOLINERA EL TEJAR", "mes_pago": "ENERO", "realizado": "", "pendiente": ""},
            {"ruta": "TEJAR", "establecimiento": "DEPOSITO LA VENTANITA II", "mes_pago": "ENERO", "realizado": "", "pendiente": ""},
            {"ruta": "TEJAR", "establecimiento": "TORTILLERIA AQUIAHUAC", "mes_pago": "MAYO", "realizado": "", "pendiente": ""},
            {"ruta": "TEJAR", "establecimiento": "ANTOJITOS VIKY", "mes_pago": "MAYO", "realizado": "", "pendiente": ""},
            {"ruta": "TEJAR", "establecimiento": "TOP VENT", "mes_pago": "MAYO", "realizado": "", "pendiente": ""},
            {"ruta": "TEJAR", "establecimiento": "SAND BLAST", "mes_pago": "ABRIL", "realizado": "", "pendiente": ""},
            {"ruta": "P. DEL TORO", "establecimiento": "RESTAURAN FELISITAS", "mes_pago": "MARZO", "realizado": "", "pendiente": ""},
            {"ruta": "P. DEL TORO", "establecimiento": "SONIGAS", "mes_pago": "MARZO", "realizado": "", "pendiente": ""},
            {"ruta": "P. CHOCOLATE", "establecimiento": "ABARROTES LA UNICA", "mes_pago": "ENERO", "realizado": "", "pendiente": ""},
            {"ruta": "LOMAS SAN GABRIEL", "establecimiento": "MADERAS Y TRIPLAY MEDELLIN", "mes_pago": "ABRIL", "realizado": "", "pendiente": ""},
            {"ruta": "LA BASCULA", "establecimiento": "ANTOJITOS EL PUNTALITO", "mes_pago": "ABRIL", "realizado": "", "pendiente": ""},
            {"ruta": "PUENTE MORENO", "establecimiento": "ABARROTES EL GÜERO", "mes_pago": "FEBRERO", "realizado": "", "pendiente": ""},
            {"ruta": "FRACC LAS PALMAS", "establecimiento": "ALPROQUIMEX", "mes_pago": "FEBRERO", "realizado": "", "pendiente": ""},
            {"ruta": "LA BOCANA", "establecimiento": "TRANSPORTES VICTOR", "mes_pago": "ABRIL", "realizado": "", "pendiente": ""},
            {"ruta": "SAN RAMON", "establecimiento": "TAQUERIA LA UNICA", "mes_pago": "MARZO", "realizado": "", "pendiente": ""}
        ]
        
        guardar_inspeccion(
            fecha_corta="2026-08-06",
            fecha_texto="JUEVES 06/AGOSTO/26",
            horario="De 10am A 2pm",
            rutas_resumen="TEJAR-P.TORO-P.CHOCOLT-LOMAS S.GABRIEL- LA BASCULA-PTE MORENO-LAS PALMAS-LA BOCANA-SAN RAMON",
            inspector="Larisa Pauleth Gonzalez Acosta",
            operador="ALBERTO VIQUEZ Ó CARLOS ALBERTO",
            items=items_ejemplo
        )
