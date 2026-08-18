import sqlite3
import os
from typing import List, Tuple, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_name: str = "directorio.db"):
        """
        Inicializa el gestor de la base de datos.
        La base de datos se crea en la ruta actual de ejecución.
        """
        self.db_path = os.path.abspath(db_name)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión activa a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        # Habilitar que las filas se retornen como diccionarios si es necesario
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Crea la tabla de contactos si no existe y realiza migraciones necesarias."""
        query = """
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT,
            empresa TEXT,
            puesto TEXT,
            direccion TEXT,
            web TEXT,
            foto TEXT
        );
        """
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(query)
                
            # Migración: Verificar si existe la columna 'foto' por si la BD ya existía sin ella
            with conn:
                try:
                    conn.execute("SELECT foto FROM contactos LIMIT 1;")
                except sqlite3.OperationalError:
                    conn.execute("ALTER TABLE contactos ADD COLUMN foto TEXT;")
        finally:
            conn.close()

    def crear_contacto(self, nombre: str, telefono: str, email: Optional[str] = None,
                       empresa: Optional[str] = None, puesto: Optional[str] = None,
                       direccion: Optional[str] = None, web: Optional[str] = None,
                       foto: Optional[str] = None) -> int:
        """
        Inserta un nuevo contacto y retorna su ID.
        """
        query = """
        INSERT INTO contactos (nombre, telefono, email, empresa, puesto, direccion, web, foto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, (nombre, telefono, email, empresa, puesto, direccion, web, foto))
                return cursor.lastrowid
        finally:
            conn.close()

    def obtener_contactos(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de todos los contactos en forma de diccionarios.
        """
        query = "SELECT * FROM contactos ORDER BY nombre ASC;"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def obtener_contacto_por_id(self, contacto_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca y retorna un contacto por su ID.
        """
        query = "SELECT * FROM contactos WHERE id = ?;"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (contacto_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def actualizar_contacto(self, contacto_id: int, nombre: str, telefono: str,
                           email: Optional[str] = None, empresa: Optional[str] = None,
                           puesto: Optional[str] = None, direccion: Optional[str] = None,
                           web: Optional[str] = None, foto: Optional[str] = None) -> bool:
        """
        Actualiza los datos de un contacto existente. Retorna True si se actualizó.
        """
        query = """
        UPDATE contactos
        SET nombre = ?, telefono = ?, email = ?, empresa = ?, puesto = ?, direccion = ?, web = ?, foto = ?
        WHERE id = ?;
        """
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, (nombre, telefono, email, empresa, puesto, direccion, web, foto, contacto_id))
                return cursor.rowcount > 0
        finally:
            conn.close()

    def eliminar_contacto(self, contacto_id: int) -> bool:
        """
        Elimina un contacto por su ID. Retorna True si se eliminó correctamente.
        """
        query = "DELETE FROM contactos WHERE id = ?;"
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, (contacto_id,))
                return cursor.rowcount > 0
        finally:
            conn.close()

    def cerrar(self):
        """Método de limpieza si fuera necesario."""
        pass
