import os
import re
import shutil
import json
from datetime import datetime
from utils import *
from win32com.client import Dispatch
from PyPDF2 import PdfMerger
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

html_features_template = os.path.join(os.getcwd(), "src", "test", "resources", "template", "overview-features.html")
html_for_each_feature_template = os.path.join(os.getcwd(), "src", "test", "resources", "template", "report-feature.html")
report_folder_path = os.path.join(os.getcwd(), "src", "test", "reports")
template_folder_path = os.path.join(os.getcwd(), "src", "test", "resources", "template")
source_files = ["logo_mibanco.png", "main.js", "style.css", "icon.ico"]
word_path1 = os.path.join(os.getcwd(), "Evidencias")
pdf_temp_path = os.path.join(os.getcwd(), "EvidenciasTEMP")
pdf_path = os.path.join(os.getcwd(), "EvidenciasPDF")
output_path = os.path.join(os.getcwd(), "output")

def process_data_json2(data_json_path):

    with open(data_json_path, 'r') as file:
        test_results = json.load(file)

    features = test_results.get("features", [])
    data = []
    for feature in features:
        feature_name = feature['name']
        scenarios = []
        scenario_passed_count = 0
        scenario_failed_count = 0
        scenario_skipped_count = 0
        step_passed_count = 0
        step_failed_count = 0
        step_skipped_count = 0

        for scenario in feature['scenarios']:
            scenario_name = scenario['name']
            status = scenario['status']
            steps = []

            if status == "passed":
                scenario_passed_count += 1
            elif status == "failed":
                scenario_failed_count += 1
            else:
                scenario_skipped_count += 1
            
            for step in scenario['steps']:
                step_name = step['name']
                
                step_keyword = step['step_type']
                step_status=step['status']
                step_message=step['text']
                step_time=step['duration']
                
                if step_status == "passed":
                    step_passed_count += 1
                elif step_status == "failed":
                    step_failed_count += 1
                else:
                    step_skipped_count += 1

                steps.append({'name': step_name,
                              'keyword': step_keyword, 
                              'status': step_status,
                              'message': step_message,
                              'duration': step_time})
                
            scenarios.append({'name': scenario_name, 
                              'status': status, 
                              'steps': steps})
            
        data.append({'feature_name': feature_name, 
                     'scenarios': scenarios,
                     'scenario_passed_count': scenario_passed_count,
                     'scenario_failed_count': scenario_failed_count,
                     'scenario_skipped_count': scenario_skipped_count,
                     'step_passed_count': step_passed_count, 
                     'step_failed_count': step_failed_count,
                     'step_skipped_count': step_skipped_count,
                     'scenarios_total': scenario_passed_count + scenario_failed_count+ scenario_skipped_count,
                     'steps_total': step_passed_count + step_failed_count + step_skipped_count})
    return data

def count_total_scenarios_and_steps(data):
    total_scenarios = 0
    total_steps = 0
    total_scenarios_passed = 0
    total_scenarios_failed = 0
    total_scenarios_skipped = 0

    for feature in data:
        total_scenarios += feature['scenarios_total']
        total_steps += feature['steps_total']
        total_scenarios_passed += feature['scenario_passed_count']
        total_scenarios_failed += feature['scenario_failed_count']
        total_scenarios_skipped += feature['scenario_skipped_count']

    scenarios_information = {'total_scenarios_passed': total_scenarios_passed,
    'total_scenarios_failed': total_scenarios_failed,
    'total_scenarios_skipped': total_scenarios_skipped}
    
    return total_scenarios, total_steps, scenarios_information

def create_report_folder2(template_folder_path, report_folder_path, source_files):
    date = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
    folder_name = f"report-{date}-paralelo"

    html_features_output = os.path.join(report_folder_path, folder_name)
    os.makedirs(html_features_output, exist_ok=True)

    # Definir las rutas a los archivos que se van a copiar
    source_folder = template_folder_path

    # Copiar los archivos
    for file_name in source_files:
        source_file_path = os.path.join(source_folder, file_name)
        destination_file_path = os.path.join(html_features_output, file_name)
        shutil.copy(source_file_path, destination_file_path)

    if os.path.exists(word_path1) and os.path.isdir(word_path1):
        print("[LOG] Si existe carpeta Evidencias Word")
        destination_file_path=os.path.join(html_features_output,"Evidencias")
        shutil.copytree(word_path1,destination_file_path)
    else:
        print("[LOG] No existe carpeta Evidencias de WOrd")

    return html_features_output

def convertir_word_a_pdf(carpeta_word, carpeta_pdf):
    """
    Convierte todos los documentos Word (.doc y .docx) en una carpeta a PDF.

    :param carpeta_word: Ruta de la carpeta que contiene los archivos Word.
    :param carpeta_pdf: Ruta de la carpeta donde se guardarán los PDFs.
    """
    # Crear la carpeta de salida si no existe
    if not os.path.exists(carpeta_pdf):
        os.makedirs(carpeta_pdf)

    # Inicializar Word
    word_app = Dispatch("Word.Application")
    word_app.Visible = False

    # Procesar cada archivo Word
    for archivo in os.listdir(carpeta_word):
        if archivo.endswith(".doc") or archivo.endswith(".docx"):
            archivo_word = os.path.join(carpeta_word, archivo)
            nombre_pdf = os.path.splitext(archivo)[0] + ".pdf"
            archivo_pdf = os.path.join(carpeta_pdf, nombre_pdf)

            try:
                print(f"[LOG] Convirtiendo: {archivo} a PDF...")
                doc = word_app.Documents.Open(archivo_word)
                doc.SaveAs(archivo_pdf, FileFormat=17)  # FileFormat=17 es el formato PDF
                doc.Close()
                print(f"[LOG] PDF guardado en: {archivo_pdf}")
            except Exception as e:
                print(f"[ERROR] No se pudo convertir {archivo} a PDF. Error: {e}")

    # Cerrar Word
    word_app.Quit()
    print("[LOG] Conversión completa.")

def obtener_clave_numerica(nombre_archivo):
    """
    Extrae la parte numérica del nombre del archivo para realizar una ordenación correcta.
    """
    # Buscar números en el nombre del archivo
    match = re.search(r'-(\d+)', nombre_archivo)
    if match:
        return int(match.group(1))
    return float('inf')  # Si no hay número, colocarlo al final

def combinar_pdfs_por_grupo(carpeta_pdf, carpeta_salida):
    """
    Combina archivos PDF en una carpeta agrupándolos por prefijo común (por ejemplo, HBK, RES).
    Genera un archivo PDF combinado para cada grupo.

    :param carpeta_pdf: Ruta de la carpeta que contiene los archivos PDF.
    :param carpeta_salida: Ruta de la carpeta donde se guardarán los PDFs combinados.
    """
    # Crear la carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Crear un diccionario para agrupar los archivos por prefijo
    grupos = {}
    for archivo in os.listdir(carpeta_pdf):
        if archivo.endswith(".pdf"):
            # Obtener el prefijo del archivo (antes del guion "-")
            prefijo = archivo.split("-")[0]
            if prefijo not in grupos:
                grupos[prefijo] = []
            grupos[prefijo].append(archivo)

    # Combinar los PDFs por grupo
    for prefijo, archivos in grupos.items():
        # Ordenar los archivos dentro del grupo por clave numérica
        archivos.sort(key=obtener_clave_numerica)
        salida_pdf = os.path.join(carpeta_salida, f"{prefijo}_combinado.pdf")
        merger = PdfMerger()

        print(f"[LOG] Combinando PDFs para el grupo '{prefijo}'...")
        for archivo in archivos:
            merger.append(os.path.join(carpeta_pdf, archivo))

        # Guardar el PDF combinado
        merger.write(salida_pdf)
        merger.close()
        print(f"[LOG] PDF combinado guardado en: {salida_pdf}")
        
    if os.path.exists(carpeta_pdf):
        try:
            shutil.rmtree(carpeta_pdf)
            print(f"[LOG] La carpeta '{carpeta_pdf}' ha sido eliminada.")
        except Exception as e:
            print(f"[ERROR] No se pudo borrar la carpeta: {e}")
    else:
        print(f"[LOG] La carpeta '{carpeta_pdf}' no existe.")

def eliminar_carpeta(carpeta_path):
    if os.path.exists(carpeta_path):
        try:
            shutil.rmtree(carpeta_path)
            print(f"[LOG] La carpeta '{carpeta_path}' ha sido eliminada.")
        except Exception as e:
            print(f"[ERROR] No se pudo borrar la carpeta: {e}")
    else:
        print(f"[LOG] La carpeta '{carpeta_path}' no existe.")

def json_to_junit2(json_input, xml_output):
    with open(json_input, 'r') as json_file:
        data = json.load(json_file)

    testsuites = Element('testsuites')
    features = data.get("features", [])
    
    for feature in features:
        testsuite = SubElement(testsuites, 'testsuite', name=feature['name'], tests=str(len(feature['scenarios'])))
        for scenario in feature['scenarios']:
            total_duration = 0
            if scenario['status'] != 'skipped':
                # Calcular la duración total de los pasos del escenario solo si no está skipped
                for step in scenario['steps']:
                    if step['status'] != 'skipped':
                        total_duration += step['duration']
            testcase = SubElement(testsuite, 'testcase', classname=feature['name'], name=scenario['name'], time=str(total_duration))
            if scenario['status'] == 'skipped':
                skipped = SubElement(testcase, 'skipped')
                skipped.text = "Scenario skipped"
            elif scenario['status'] != 'passed':
                failure = SubElement(testcase, 'failure', message="Test failed")
                failure.text = scenario['name']
            for step in scenario['steps']:
                if scenario['status'] == 'skipped' or ('result' in step and step['status'] == 'skipped'):
                    if not 'skipped' in testcase.attrib:
                        skipped = SubElement(testcase, 'skipped')
                        skipped.text = "Step skipped"
                elif 'result' in step and step['status'] != 'passed':
                    failure = SubElement(testcase, 'failure', message="Step failed")
                    failure.text = step['name']

    raw_xml = tostring(testsuites, 'utf-8')
    pretty_xml = parseString(raw_xml).toprettyxml(indent="  ")

    with open(xml_output, 'w') as xml_file:
        xml_file.write(pretty_xml)

#convertir_word_a_pdf(word_path1,pdf_temp_path)
#combinar_pdfs_por_grupo(pdf_temp_path,pdf_path)
data_json_path= os.path.join(os.getcwd(), "output","report.json")
# Convertir archivo json en formato junit xml para integración con Azure DevOps
json_to_junit2(data_json_path, 'output.xml')
data = process_data_json2(data_json_path)
total_scenarios, total_steps, scenarios_information= count_total_scenarios_and_steps(data)
report_folder = create_report_folder2(template_folder_path, report_folder_path, source_files)
# --- TOOK GLOBAL CONSISTENTE ---
import os
import time
import datetime as dt
took_str = "N/A"
try:
    start_time_path = os.path.join(os.getcwd(), 'start_time.txt')
    if os.path.exists(start_time_path):
        with open(start_time_path, 'r') as f:
            start_time = float(f.read())
        end_time = time.time()
        took_seconds = end_time - start_time
        took_str = str(dt.timedelta(seconds=int(took_seconds)))
except Exception as e:
    print(f"[DEBUG] No se pudo calcular took global: {e}")
generate_html_for_all_features(html_features_template, report_folder, data, total_scenarios, total_steps, scenarios_information, took=took_str)
generate_html_for_each_feature(html_for_each_feature_template, report_folder, data)
eliminar_carpeta(word_path1)
eliminar_carpeta(pdf_path)
eliminar_carpeta(output_path)