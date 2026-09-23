import sqlite3
import pandas as pd

def renumerar():
    conn = sqlite3.connect('whatsapp_messages.db')
    cursor = conn.cursor()

    df = pd.read_sql_query('SELECT * FROM servicios_anuales_2026 ORDER BY mes_num ASC, fecha ASC, hora ASC', conn)
    print(f"Total registros cargados: {len(df)}")

    cursor.execute('DROP TABLE IF EXISTS servicios_anuales_2026')
    cursor.execute('''
        CREATE TABLE servicios_anuales_2026 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT,
            mes_num INTEGER,
            fecha TEXT,
            hora TEXT,
            categoria_macro TEXT,
            subtipo_servicio TEXT,
            localidad TEXT,
            efectividad TEXT,
            fuente_datos TEXT,
            resumen_servicio TEXT
        )
    ''')

    for idx, (_, r) in enumerate(df.iterrows(), start=1):
        cursor.execute('''
            INSERT INTO servicios_anuales_2026 
            (id, mes, mes_num, fecha, hora, categoria_macro, subtipo_servicio, localidad, efectividad, fuente_datos, resumen_servicio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            idx, r['mes'], int(r['mes_num']), r['fecha'], r['hora'],
            r['categoria_macro'], r['subtipo_servicio'], r['localidad'],
            r['efectividad'], r['fuente_datos'], r['resumen_servicio']
        ))

    conn.commit()

    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'servicios_anuales_2026'")
    cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('servicios_anuales_2026', ?)", (len(df),))
    conn.commit()

    cursor.execute('SELECT MIN(id), MAX(id), COUNT(*) FROM servicios_anuales_2026')
    res = cursor.fetchone()
    print(f"Resultado: Min ID = {res[0]}, Max ID = {res[1]}, Total = {res[2]}")

    df_check = pd.read_sql_query('SELECT id, mes, fecha, subtipo_servicio FROM servicios_anuales_2026 LIMIT 5', conn)
    print("\nPrimeras 5 filas en Enero:")
    print(df_check.to_string())

    conn.close()

if __name__ == '__main__':
    renumerar()
