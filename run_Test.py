import sys
import subprocess

def print_banner():
    DARK_GREEN = "\033[32m"
    RESET = "\033[0m"
    print(DARK_GREEN + r"""
 ================================================================
 ****************************************************************
 **    _______  _____    _______     ______  _____   _____     **
 **   |   _   ||     |_ |     __|   |   __ \|     \ |     \    **
 **   |       ||       ||__     |   |   __ <|  --  ||  --  |   **
 **   |___|___||_______||_______|   |______/|_____/ |_____/    **
 **                                                            **
 ****************************************************************
 ************ Automated Lab Suite BDD - QA Framework ************
 ================================================================
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
