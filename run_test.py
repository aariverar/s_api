import sys
import subprocess
from datetime import datetime
import os

def print_banner():
    DARK_GREEN = "\033[32m"
    GRAY = "\033[90m"
    RESET = "\033[0m"
    
    # Get current timestamp and system info
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    computer_name = os.environ.get('COMPUTERNAME', 'Unknown')
    username = os.environ.get('USERNAME', 'Unknown')
    
    print(DARK_GREEN + r"""
 ================================================================
 ****************************************************************
 **    _______  __       _______     ______  _____   _____     **
 **   |   _   ||  |     |    ___|   |  ___ \|     \ |     \    **
 **   |       ||  |____ |___    |   |  ___ <|  --  ||  --  |   **
 **   |___|___||_______||_______|   |______/|_____/ |_____/    **
 **                                                            **
 ****************************************************************
 ************ Automated Lab Suite BDD - QA Framework ************
 ================================================================
    """ + RESET)
    
    print(GRAY + f"""
 Started at: {current_time}
 Executed in: {computer_name}
 Executed by: {username}
    """ + RESET)


def get_behave_command():
    """
    Detecta automáticamente la ubicación correcta de behave
    """
    import shutil
    
    # 1. Intentar ubicaciones específicas de Python 3.12 y verificar que funcionen
    possible_paths = [
        r"C:\Program Files\Python312\Scripts\behave.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\Scripts\behave.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            # Verificar que realmente funciona ejecutándolo
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✓ Behave encontrado y funcional en: {path}")
                    return f'"{path}"'
                else:
                    print(f"⚠️  Behave encontrado pero no funcional en: {path}")
            except:
                print(f"⚠️  Behave encontrado pero no ejecutable en: {path}")
    
    # 2. Verificar si behave está en el PATH y funciona
    behave_path = shutil.which("behave")
    if behave_path:
        try:
            result = subprocess.run(["behave", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ Behave encontrado y funcional en PATH: {behave_path}")
                return "behave"
            else:
                print(f"⚠️  Behave encontrado en PATH pero no funcional: {behave_path}")
        except:
            print(f"⚠️  Behave encontrado en PATH pero no ejecutable: {behave_path}")
    
    # 3. Usar python -m behave como fallback
    try:
        result = subprocess.run([sys.executable, "-m", "behave", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Behave disponible y funcional vía 'python -m behave'")
            return f'"{sys.executable}" -m behave'
        else:
            print("⚠️  'python -m behave' no funciona correctamente")
    except:
        print("⚠️  Error al probar 'python -m behave'")
    
    # 4. Si nada funciona, mostrar error detallado
    print("❌ ERROR: No se encontró behave instalado y funcional")
    print("\nUbicaciones verificadas:")
    for path in possible_paths:
        exists = "✓" if os.path.exists(path) else "✗"
        print(f"  {exists} {path}")
    
    behave_in_path = "✓" if shutil.which("behave") else "✗"
    print(f"  {behave_in_path} behave en PATH del sistema")
    
    print(f"  ✗ python -m behave")
    print("\nPor favor verifique que behave esté instalado correctamente:")
    print("  pip install behave==1.2.6")
    return None


def main():
    print_banner()
    
    # Detectar ubicación de behave
    behave_cmd = get_behave_command()
    if not behave_cmd:
        input("Presione Enter para salir...")
        sys.exit(1)
    
    default_tag = "@Santander"
    if len(sys.argv) > 1:
        tag = sys.argv[1]
    else:
        tag = input(f"Ingresa el tag a ejecutar (por defecto {default_tag}): ")
        if not tag.strip():
            tag = default_tag
    
    cmd = f"{behave_cmd} --tags={tag} --no-capture"
    print(f"Ejecutando: {cmd}")
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main()
