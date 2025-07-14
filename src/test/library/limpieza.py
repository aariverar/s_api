import os
import shutil
import glob


def safe_remove(path, retries=3):
    """
    Intenta eliminar un archivo o carpeta hasta 'retries' veces, esperando si está bloqueado.
    """
    import time
    for attempt in range(retries):
        try:
            if os.path.isfile(path):
                os.remove(path)
                return
            elif os.path.isdir(path):
                shutil.rmtree(path)
                return
        except PermissionError as e:
            print(f'[LIMPIEZA] Permiso denegado al eliminar {path} (intento {attempt+1}/{retries}): {e}')
            time.sleep(1)
        except Exception as e:
            print(f'[LIMPIEZA] No se pudo eliminar {path} (intento {attempt+1}/{retries}): {e}')
            time.sleep(1)
    print(f'[LIMPIEZA] No se pudo eliminar {path} tras {retries} intentos.')

# Eliminar start_time.txt
txt_path = os.path.join(os.getcwd(), 'start_time.txt')
safe_remove(txt_path)


# Eliminar __pycache__ y .pyc usando rutas absolutas y logs claros
root_dir = os.getcwd()
for pyc in glob.glob(os.path.join(root_dir, '**', '*.pyc'), recursive=True):
    print(f'[LIMPIEZA] Eliminando archivo pyc: {pyc}')
    safe_remove(pyc)
for cache_dir in glob.glob(os.path.join(root_dir, '**', '__pycache__'), recursive=True):
    print(f'[LIMPIEZA] Eliminando carpeta __pycache__: {cache_dir}')
    safe_remove(cache_dir)


# Eliminar evidencias y la carpeta si queda vacía
EVID_DIR = os.path.join(os.getcwd(), 'Evidencias')
if os.path.exists(EVID_DIR):
    for f in os.listdir(EVID_DIR):
        safe_remove(os.path.join(EVID_DIR, f))
    # Intentar eliminar la carpeta si queda vacía
    try:
        if not os.listdir(EVID_DIR):
            print(f'[LIMPIEZA] Eliminando carpeta vacía Evidencias: {EVID_DIR}')
            os.rmdir(EVID_DIR)
    except Exception as e:
        print(f'[LIMPIEZA] No se pudo eliminar la carpeta Evidencias: {e}')

print('[LIMPIEZA] Archivos temporales y evidencias eliminados.')
