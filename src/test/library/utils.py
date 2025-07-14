import json
import os
import shutil
from datetime import datetime
from jinja2 import Template
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import requests
import xml.etree.ElementTree as ET
import re
import difflib
"""
    Función para generar reporte HTML (overview-features)
"""
def generate_html_for_all_features(template, output_path, data, scenarios, steps, scenarios_information, took=None):

    with open(template, 'r', encoding='utf-8') as file:
        template_content = file.read()
    template = Template(template_content)

    # Formatear la fecha y hora según el formato especificado
    execution_time = datetime.now()
    formato = "%d %b %Y, %H:%M"
    fecha_formateada = execution_time.strftime(formato)

    total_features = len(data)
    total_duration, average_duration = sum_durations_and_average_duration(data)

    html_output = template.render(features=data, 
                                  total_features=total_features, 
                                  total_scenarios=scenarios, 
                                  total_steps=steps, 
                                  scenarios_information=scenarios_information,
                                  date=fecha_formateada,
                                  total_duration=total_duration,
                                  average_duration=average_duration,
                                  took=str(took) if took else "N/A")
    
    # Write the HTML output to a file
    output_path = os.path.join(output_path,"overview-features.html")
   
    with open(output_path, 'w', encoding='utf-8' ) as file:
        file.write(html_output)

"""
    Función para generar reporte HTML (report-feature-1, report-feature-2, ...)
"""

def generate_html_for_each_feature(template, output_path, data):

    with open(template, 'r') as file:
        template_content = file.read()
    template = Template(template_content)

    # Formatear la fecha y hora según el formato especificado
    execution_time = datetime.now()
    formato = "%d %b %Y, %H:%M"
    fecha_formateada = execution_time.strftime(formato)

    for index, feature in enumerate(data):

        html_output = template.render(feature=feature,
                                      feature_index=index, 
                                      date=fecha_formateada)
        
        # Añadir el índice al nombre del archivo
        output_file = os.path.join(output_path, f"report-feature-{index+1}.html")

        # Write the HTML output to a file
        with open(output_file, 'w') as file:
            file.write(html_output)

def process_data_json(data_json_path):

    with open(data_json_path, 'r') as file:
        test_results = json.load(file)

    data = []
    for feature in test_results:
        feature_name = feature['name']
        scenarios = []
        scenario_passed_count = 0
        scenario_failed_count = 0
        scenario_skipped_count = 0
        step_passed_count = 0
        step_failed_count = 0
        step_skipped_count = 0

        for scenario in feature['elements']:
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
                step_keyword = step['keyword']

                if 'result' in step:
                    step_status = step['result'].get('status', 'unknown') 
                    step_message = step['result'].get('message', '')
                    step_time = step['result'].get('duration', 0)
                else:
                    step_status = 'failed'
                    step_message = 'failed'
                    step_time = 0
                
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

def create_report_folder(template_folder_path, report_folder_path, source_files, word_path):
    date = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
    folder_name = f"report-{date}"

    html_features_output = os.path.join(report_folder_path, folder_name)
    os.makedirs(html_features_output, exist_ok=True)

    # Definir las rutas a los archivos que se van a copiar
    source_folder = template_folder_path

    # Copiar los archivos
    for file_name in source_files:
        source_file_path = os.path.join(source_folder, file_name)
        destination_file_path = os.path.join(html_features_output, file_name)
        shutil.copy(source_file_path, destination_file_path)


    destination_file_path = os.path.join(html_features_output, "Evidencias")
    shutil.copytree(word_path, destination_file_path)

    return html_features_output

def sum_durations_and_average_duration(data):
    total_duration = 0
    scenario_count = 0
    for feature in data:
        for scenario in feature['scenarios']:
            if scenario['status'] != 'skipped':
                for step in scenario['steps']:
                    total_duration += step['duration']
                scenario_count += 1 # ignore scenario skipped
    if scenario_count == 0:
        return "0s", "0s"
    
    average_duration = total_duration / scenario_count
    total_duration_str = str(round(total_duration, 2)) + "s"
    average_duration_str = str(round(average_duration, 2)) + "s"

    return total_duration_str, average_duration_str

def modify_json_with_message(json_data,step_messages,scenario_newNames):
    for feature in json_data:
        for element in feature.get('elements', []):
            for names in scenario_newNames:
                if element['name']==names['scenario_name']:
                    #Cambiar el nombre de los escenarios
                    element['name']=names['scenario_new_name']
            for step in element.get('steps', []):
                # Buscar el mensaje correspondiente para este step
                for msg in step_messages:
                    if msg['step_name'] == step['name']:
                        # Añadir el mensaje personalizado al step
                        if 'result' in step:
                            step['result']['message'] = msg['message']
                        break
    return json_data

""" 
    Funcion que convierte un archivo JSON en un archivo JUnit XML para usar en pipelines de Azure DevOps
"""
def json_to_junit(json_input, xml_output):
    with open(json_input, 'r') as json_file:
        data = json.load(json_file)

    testsuites = Element('testsuites')
    for feature in data:
        testsuite = SubElement(testsuites, 'testsuite', name=feature['name'], tests=str(len(feature['elements'])))
        for scenario in feature['elements']:
            total_duration = 0
            if scenario['status'] != 'skipped':
                # Calcular la duración total de los pasos del escenario solo si no está skipped
                for step in scenario['steps']:
                    if 'result' in step and step['result']['status'] != 'skipped':
                        total_duration += step['result']['duration']
            testcase = SubElement(testsuite, 'testcase', classname=feature['name'], name=scenario['name'], time=str(total_duration))
            if scenario['status'] == 'skipped':
                skipped = SubElement(testcase, 'skipped')
                skipped.text = "Scenario skipped"
            elif scenario['status'] != 'passed':
                failure = SubElement(testcase, 'failure', message="Test failed")
                failure.text = scenario['name']
            for step in scenario['steps']:
                if scenario['status'] == 'skipped' or ('result' in step and step['result']['status'] == 'skipped'):
                    if not 'skipped' in testcase.attrib:
                        skipped = SubElement(testcase, 'skipped')
                        skipped.text = "Step skipped"
                elif 'result' in step and step['result']['status'] != 'passed':
                    failure = SubElement(testcase, 'failure', message="Step failed")
                    failure.text = step['name']

    raw_xml = tostring(testsuites, 'utf-8')
    pretty_xml = parseString(raw_xml).toprettyxml(indent="  ")

    with open(xml_output, 'w') as xml_file:
        xml_file.write(pretty_xml)

def convert_headers_to_dict(headers):
    return {key: value for key, value in headers.items()}

# Función para mostrar los encabezados en formato pretty
def pretty_print_headers(headers):
    # Convertir a un diccionario estándar si es un CaseInsensitiveDict
    if isinstance(headers, requests.structures.CaseInsensitiveDict):
        headers = convert_headers_to_dict(headers)
    pretty_headers = json.dumps(headers, indent=4)
    return pretty_headers

def pretty_print_xml(xml_str):
    try:
        root = ET.fromstring(xml_str)
        pretty_xml = ET.tostring(root, encoding='unicode', method='xml')
        return pretty_xml
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"

def pretty_print_xml2(xml_str):
    try:
        dom = parseString(xml_str)
        return dom.toprettyxml(indent=" ")
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"
    
def get_tag_value(tags, prefix):    
    #Busca un tag que comience con el prefijo y extrae su valor.
    return next((re.sub(f"^{prefix}", "", tag) for tag in tags if tag.startswith(prefix)), None)

def highlight_differences(expected, actual):
    diff = difflib.ndiff(expected.splitlines(), actual.splitlines())
    highlighted_diff = []
    for line in diff:
        if line.startswith('-'):
            highlighted_diff.append(f'<span style="color: red;">Expected Content: {line[2:]}</span>')
        elif line.startswith('+'):
            highlighted_diff.append(f'<span style="color: green;">Actual Content: {line[2:]}</span>')
        elif line.startswith('?'):
            continue  # Omitir líneas con '?'
        else:
            highlighted_diff.append(f'    {line[2:]}')
    return '<br>'.join(highlighted_diff)