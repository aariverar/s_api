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


def main():
    print_banner()
    default_tag = "@Santander"
    if len(sys.argv) > 1:
        tag = sys.argv[1]
    else:
        tag = input(f"Ingresa el tag a ejecutar (por defecto {default_tag}): ")
        if not tag.strip():
            tag = default_tag
    cmd = f"behave --tags={tag} --no-capture"
    print(f"Ejecutando: {cmd}")
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main()
