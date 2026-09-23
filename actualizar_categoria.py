import sqlite3

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("UPDATE servicios_anuales_2026 SET categoria_macro = 'Agentes Perturbadores' WHERE categoria_macro = 'Rescate / Desastres Naturales'")
print(f"Filas actualizadas a Agentes Perturbadores: {c.rowcount}")
conn.commit()
conn.close()
