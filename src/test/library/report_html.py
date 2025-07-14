import os
import time
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

"""
    Este script es para tomar capturas de pantalla del reporte HTML para envío de correo con Azure Pipeline
"""

base_path = "src/test/reports" # Ruta base de los reportes
output_path = os.path.join(os.getcwd(), "src/test/resources/email") # Ruta donde se guardará la captura de pantalla
driver_path = os.path.join(os.getcwd(),"src/test/resources/drivers/chrome/126.0/chromedriver.exe") # OJO Ruta del chromedriver, cambiar si es necesario

# Verificar y crear el directorio de salida si no existe
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Buscar el directorio que empieza con "report-"
report_dirs = glob.glob(os.path.join(base_path, 'report-*'))

if not report_dirs:
    raise FileNotFoundError("No se encontró ningún directorio que empiece con 'report-'")

report_dir = report_dirs[0]

# Ruta del archivo HTML
html_file_path = os.path.join(report_dir, 'overview-features.html')
if not os.path.exists(html_file_path):
    raise FileNotFoundError(f"No se encontró el archivo {html_file_path}")

# Configuración de Selenium
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

# Inicializar el navegador
service = Service(driver_path)  # Reemplaza con la ruta a tu chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

try:

    driver.get(f'file://{os.path.abspath(html_file_path)}')

    # Esperar 3 segundos para que el archivo cargue completamente
    time.sleep(3)
    
    # Reducir el tamaño del contenido al 50%
    # body = driver.find_element(By.TAG_NAME, 'body')
    # driver.execute_script("arguments[0].style.transform = 'scale(0.5)'; arguments[0].style.transformOrigin = '0 0';", body)
    
    # Tomar captura de pantalla
    screenshot_path = os.path.join(output_path, 'reporte.png')
    driver.save_screenshot(screenshot_path)
    
    print(f"Captura de pantalla guardada en: {screenshot_path}")
finally:
    driver.quit()