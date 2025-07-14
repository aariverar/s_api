import json
import os
import re
import configparser
from datetime import datetime
from src.test.library.utils import *
from src.test.library.variables import *
from src.test.library.excel_reader import data
import src.test.library.word_generate as generateWord
from datetime import datetime
from src.test.library.util_api import UTIL_API
from behave.model_core import Status
from src.test.library.storage_connection import *
import time

def before_all(context):
    # Inicialización de variables de contexto para la ejecución
    context.step_messages = []  # Mensajes personalizados de steps para el reporte
    context.newNames = []       # Nombres alternativos de escenarios (por ejemplo, si se renombran dinámicamente)
    context.start_time = datetime.now()
    context.hostname = os.environ.get('COMPUTERNAME', '')
    formato = "%d %b %Y, %H:%M"
    context.fecha_formateada = context.start_time.strftime(formato)
    # Leer configuración general del proyecto
    config = configparser.ConfigParser()
    config.read('service.properties')
    context.log = config.get('General', 'log')
    context.proyecto = config.get('General', 'Proyecto')
    context.ciclo = config.get('General', 'Ciclo')
    context.tipoWord = config.get('General', 'Word')
    # Inicializar cliente de base de datos si corresponde
    if context.log.lower() == 'true':
        context.table_client = get_table_client()
    # Crear archivo de tiempo de inicio si no existe (para cálculo de duración total en paralelo)
    if not os.path.exists('start_time.txt'):
        with open('start_time.txt', 'w') as f:
            f.write(str(time.time()))
    
def after_all(context):
    try:
        # Calcular duración total de la ejecución (compatible con ejecución paralela)
        try:
            with open('start_time.txt', 'r') as f:
                start_time = float(f.read())
            end_time = time.time()
            import datetime as dt
            took_seconds = end_time - start_time
            took_str = str(dt.timedelta(seconds=int(took_seconds)))
        except Exception:
            took_str = "N/A"
        # Mostrar ruta de evidencia si existe
        if hasattr(context, 'evidence_path'):
            print(f"[DEBUG] context.evidence_path: {getattr(context, 'evidence_path', None)}")
        # Cerrar el JSON de resultados y cargar datos
        data_json_path = os.path.join(os.getcwd(), "json.pretty.output")
        with open(data_json_path, "a") as json_file:
            json_file.write("]")
        with open(data_json_path, 'r') as file:
            data = json.load(file)
        # Modificar nombres de steps y escenarios en el JSON para el reporte
        modified_data = modify_json_with_message(data, context.step_messages, context.newNames)
        data_json_path = os.path.join(os.getcwd(), "New.pretty.output")
        with open(data_json_path, 'w') as file:
            json.dump(modified_data, file, indent=4)
        # Generar reporte HTML principal y por feature
        data_json_path = os.path.join(os.getcwd(), "New.pretty.output")
        data = process_data_json(data_json_path)
        total_scenarios, total_steps, scenarios_information = count_total_scenarios_and_steps(data)
        report_folder = create_report_folder(template_folder_path, report_folder_path, source_files, word_path1)
        generate_html_for_all_features(html_features_template, report_folder, data, total_scenarios, total_steps, scenarios_information, took=took_str)
        if os.path.exists('start_time.txt'):
            os.remove('start_time.txt')
        generate_html_for_each_feature(html_for_each_feature_template, report_folder, data)
        # Generar reporte JUnit XML para integración continua
        json_to_junit('json.pretty.output', 'output.xml')
        # Limpiar carpeta temporal de evidencias Word si existe
        if os.path.exists(word_path1):
            shutil.rmtree(word_path1)
            print(f"La carpeta '{word_path1}' ha sido borrada.")
        else:
            print(f"La carpeta '{word_path1}' no existe.")
    except Exception as e:
        print(f"[ERROR][after_all] Excepción inesperada: {e}", flush=True)


def before_feature(context, feature):
    # Hook para lógica previa a cada feature (opcional)
    pass


def after_feature(context, feature):
    # Hook para lógica posterior a cada feature (opcional)
    pass


def before_scenario(context, scenario):
    # Inicializa el tiempo de inicio y el estado del escenario
    context.start_time = datetime.now()
    context.state = None

    
def after_scenario(context, scenario):
    try:
        # Si el escenario no se ejecutó, márcalo como omitido y registra el nombre alternativo
        if context.state is not None:
            scenario.set_status("skipped")
            scenario_NewName = {
                'scenario_name': scenario.name,
                'scenario_new_name': "Escenario Skipeado"
            }
            context.newNames.append(scenario_NewName)
        else:
            # Si se usa evidencia individual, actualiza el estado en el Word
            if context.tipoWord == "Individual":
                generateWord.set_status_scenario(scenario.status.name, context)
        # Guardar resultados del escenario en la base de datos si corresponde
        if context.log.lower() == 'true':
            try:
                context.end_time = datetime.now()
                context.timer = context.end_time - context.start_time
                context.estado = str(scenario.status).split('.')[-1].capitalize()
                save_to_table(context, scenario)
            except Exception as e:
                print(f"Error al guardar datos del escenario en la base de datos: {e}")
        # Si el escenario fue renombrado dinámicamente, actualiza el nombre en la evidencia
        if hasattr(context, 'nameEscenario'):
            scenario_NewName = {
                'scenario_name': scenario.name,
                'scenario_new_name': context.nameEscenario
            }
            context.newNames.append(scenario_NewName)
            scenario.name = context.nameEscenario
        print(f"[DEBUG] after_scenario terminado para: {scenario.name}")
        # Cierra el documento Word si está abierto (según el tipo de objeto)
        if hasattr(context, 'xdoc'):
            try:
                if hasattr(context.xdoc, 'Close'):
                    context.xdoc.Close()
                elif hasattr(context.xdoc, 'quit'):
                    context.xdoc.quit()
                elif hasattr(context.xdoc, 'Quit'):
                    context.xdoc.Quit()
                print("[DEBUG] Documento Word cerrado correctamente.")
            except Exception as e:
                print(f"[DEBUG] Error al cerrar Word: {e}")
        print("[DEBUG] after_all terminado. Revisa el reporte HTML generado en la carpeta de reportes.")
    except Exception as e:
        print(f"[ERROR][after_scenario] Excepción inesperada: {e}", flush=True)
    

def before_step(context, step):
    # Hook para lógica previa a cada step (opcional)
    pass

def after_step(context, step):
    # Si el step no se ejecuta, márcalo como omitido y registra el mensaje personalizado
    if context.ejecutar == "NO":
        context.custom_message = "NO-EXECUTED"
        step.status = Status.skipped
    if hasattr(context, 'custom_message'):
        step_message = {
            'scenario_name': context.nameEscenario,
            'step_name': step.name,
            'message': context.custom_message
        }
        context.step_messages.append(step_message)
        step.text = context.custom_message
    # Log de steps fallidos
    if step.status == "failed":
        print(f"Step failed: {step.name}")