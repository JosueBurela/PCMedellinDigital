import os
import shutil
from typing import Tuple

SQLITE_HEADER = b'SQLite format 3\x00'

def validar_base_datos(filepath: str) -> bool:
    """
    Verifica si un archivo existe y contiene la firma/encabezado de SQLite3.
    """
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)
            return header == SQLITE_HEADER
    except Exception:
        return False

def exportar_respaldo(db_source_path: str, dest_path: str) -> Tuple[bool, str]:
    """
    Copia la base de datos activa a la ubicación de destino seleccionada por el usuario.
    Retorna (True, mensaje_exito) o (False, mensaje_error).
    """
    if not os.path.exists(db_source_path):
        return False, "La base de datos original no existe."
    
    try:
        # Asegurarse que el directorio destino exista
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        shutil.copy2(db_source_path, dest_path)
        return True, f"Respaldo exportado exitosamente a: {dest_path}"
    except Exception as e:
        return False, f"Error al exportar respaldo: {str(e)}"

def importar_respaldo(src_path: str, db_target_path: str) -> Tuple[bool, str]:
    """
    Valida un archivo de respaldo y reemplaza la base de datos activa con él.
    Retorna (True, mensaje_exito) o (False, mensaje_error).
    """
    # 1. Validar si el archivo de respaldo existe y es una base de datos válida
    if not os.path.exists(src_path):
        return False, "El archivo de respaldo seleccionado no existe."
        
    if not validar_base_datos(src_path):
        return False, "El archivo seleccionado no es una base de datos SQLite válida."
    
    try:
        # 2. Reemplazar la base de datos actual
        # Intentamos remover el archivo destino si existe por precaución o simplemente shutil lo sobrescribe
        shutil.copy2(src_path, db_target_path)
        return True, "Base de datos restaurada exitosamente."
    except Exception as e:
        return False, f"Error al importar respaldo: {str(e)}"
