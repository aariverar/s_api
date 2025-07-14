import os
import json
from selenium.webdriver import Chrome, Firefox, Edge
import configparser
from openpyxl import Workbook, load_workbook
from src.test.library.excel_reader import data
import requests
from src.test.library.word_generate import *
from src.test.library.utils import *
from src.test.library.timestamp_validator import validate_dynamic_timestamp
import xml.etree.ElementTree as ET
import time

class UTIL_API:
    def __init__(self, context):
        self.context = context
    
    def get_data(self):
        return data(self.context.excel,self.context.hoja)
    
    def get_ejecucion(self,datos):
        return self.get_data()[int(datos)-1]["Ejecucion"]

    def lectura_excel(self,datos):
        try:
            self.context.endpoint = self.get_data()[int(datos)-1]["Endpoint"]
            self.context.nameEscenario = self.get_data()[int(datos)-1]["Escenario"]
            self.context.iteracion = self.get_data()[int(datos)-1]["Iteracion"]
            self.context.nameApi = self.get_data()[int(datos)-1]["Api"]

            if self.get_data()[int(datos)-1]["Headers"]:
                self.context.headers_string = self.get_data()[int(datos)-1]["Headers"]
                headers_list = self.context.headers_string.split('\n')
                # Asegurarse de que cada línea dividida tenga exactamente dos elementos
                split_headers = [header.split(': ', 1) if ': ' in header else [header, ''] for header in headers_list]
                self.context.headers = dict(split_headers)
            else:
                self.context.headers_string=''
                self.context.headers=''
            if self.get_data()[int(datos)-1]["Params"]:
                self.context.params = dict([Params.split(': ') for Params in (self.get_data()[int(datos)-1]["Params"]).split('\n')])
            else:
                self.context.params=''
            if self.get_data()[int(datos)-1]["Body"]:
                self.context.body=self.get_data()[int(datos)-1]["Body"]
            else:
                self.context.body=''
            if self.get_data()[int(datos)-1]["Expected Headers Response"]:
                self.context.expected_headers= self.get_data()[int(datos)-1]["Expected Headers Response"]
            else:
                self.context.expected_headers=''
            if self.get_data()[int(datos)-1]["Expected Response"]:
                self.context.expected_response= self.get_data()[int(datos)-1]["Expected Response"]
            else:
                self.context.expected_response=''
            self.context.request_type = self.get_data()[int(datos)-1]["Request Type"]
            self.context.expected_status_code = self.get_data()[int(datos)-1]["Expected Status Code"]
            self.context.expected_content = self.get_data()[int(datos)-1]["Expected Content_1"]
            self.context.custom_message = f"Se extrae: \nEndpoint: {self.context.endpoint}"
            self.context.rutaEvidencia = os.path.join(os.getcwd(),"Evidencias",f"{self.context.nameApi}.docx")
            if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Individual":
                print("[LOG] No se generará Word")
            else:
                self.context.xdoc= start_up_word(self.context.rutaEvidencia)
                if self.context.iteracion == '1':
                    crear_tabla_inicio(self.context.xdoc,context=self.context)
        except Exception as e:            
            print(f"Ocurrio un error inesperado en lectura_excel() {e}")
            self.context.custom_message=f"Ocurrio un error inesperado en lectura_excel() {e}"
            raise AssertionError(f"Ocurrio un error inesperado en lectura_excel() {e}")

    def enviar_peticion(self,endpoint='',method='GET',headers='',params='',body='',anidadoB=None,anidadoH=None,log=True,logWord=True):
        try:
            if not endpoint:                
                endpoint = self.context.endpoint
                headers=self.context.headers
                params=self.context.params
                body=self.context.body
                method=self.context.request_type
                print(method)
            print("[LOG] Se envia la peticion")
            if anidadoH:
                for key, value in anidadoH.items():
                    headers[key] = value
            if method == 'GET': 
                if body:
                    responseData = requests.get(endpoint, headers=headers,data=body,params=params,verify=False)
                else:
                    responseData = requests.get(endpoint, headers=headers,params=params,verify=False)
            elif method in ['POST', 'PUT']:
                if body:
                    if str(body).strip().startswith('<'):
                        responseData = requests.request(
                            method,
                            endpoint,
                            headers=headers,
                            params=params,
                            data=body,
                            verify=False
                        )
                    else:
                        if not isinstance(body,dict):
                            body = json.loads(body)
                        if anidadoB:
                            for key, value in anidadoB.items():
                                body[key] = value
                        responseData = requests.request(
                            method,
                            endpoint,
                            headers=headers,
                            params=params,
                            json=body,
                            verify=False
                        )
                else:
                    responseData = requests.request(
                        method,
                        endpoint,
                        headers=headers,
                        params=params,
                        verify=False
                    ) 
            else:
                raise ValueError(f"Unsupported request type: {method}")
            if log:
                log_messages = "\n<strong>REQUEST:</strong>\n"
                log_messages += f"{method} {responseData.url}\n"
                log_messages += f"Request Headers: {pretty_print_headers(responseData.request.headers)}\n"
                self.context.custom_message=log_messages
                if params:
                    log_messages += f"Params: {pretty_print_headers(params)}\n"
                if body:
                    print(self.context.body)
                    if str(body).strip().startswith('<'):
                        log_messages += f"Body: {pretty_print_xml(body)}"
                        bodyWord = pretty_print_xml(body)
                    else:
                        log_messages += f"Body: {pretty_print_headers(body)}"
                        bodyWord = pretty_print_headers(body)
                else:
                    bodyWord = ""
                
                self.context.custom_message=log_messages
                log_messages += "\n\n<strong>RESPONSE:</strong>\n"
                log_messages += f"{responseData.request.method} - Code: {responseData.status_code} {responseData.reason}\n"
                self.context.custom_message=log_messages
                log_messages += f"Headers: {pretty_print_headers(responseData.headers)}\n"
                self.context.custom_message=log_messages
                log_messages += f"Elapsed Time: {responseData.elapsed}\n"
                if responseData.text.strip() == "":
                    log_messages += "Response Empty\n"
                    responseWord = "Response Empty"
                else:
                    if 'json' in responseData.headers.get('Content-Type', ''):
                        log_messages += f"{pretty_print_headers(responseData.json())}\n"
                        responseWord = pretty_print_headers(responseData.json())
                    elif "text/xml" in responseData.headers.get('Content-Type', ''):
                        log_messages += f"{pretty_print_xml2(responseData.text)}\n"
                        responseWord = pretty_print_xml2(responseData.text)
                    else:
                        log_messages += f"{responseData.text}\n"
                        responseWord = responseData.text

                self.context.custom_message = log_messages
                if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Individual":
                   print("[LOG] No se generará Word")
                else: 
                    if logWord:
                        header_formateado=json.dumps(headers,indent=4)
                        crear_tabla_response(self.context.xdoc,self.context.iteracion,self.context.nameEscenario,method,endpoint,str(responseData.status_code),responseData.reason,str(header_formateado),bodyWord,responseWord,str(responseData.elapsed))
                        guardarWord(self.context.xdoc,self.context.rutaEvidencia)
            return responseData
        except Exception as e:
            print("[LOG] Error realizar la peticion:",e)
            self.context.custom_message =f"Error realizar la peticion:{e}{self.context.custom_message}"
            raise AssertionError("[LOG] Error al realizar la peticion")
    
    def validacion_status_code(self,responseData):
        try:
            self.context.custom_message =""
            print("[LOG] Se valida el status Code")
            print(f"Expected Status Code: {self.context.expected_status_code}")
            print(f"Actual Status Code: {responseData.status_code}")
            log_messages = ""
            log_messages += "[LOG] Se valida el status Code\n"
            log_messages += f"Expected Status Code: {self.context.expected_status_code}\n"
            log_messages += f"Actual Status Code: {responseData.status_code}\n"
            self.context.custom_message = log_messages
            assert str(responseData.status_code) == str(self.context.expected_status_code)
            if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Invidivual":
                print("[LOG] No se generará Word")
            else:
                crear_tabla_validacion(self.context.xdoc,self.context.iteracion,"PASSED",str(self.context.expected_status_code),str(responseData.status_code))
                guardarWord(self.context.xdoc,self.context.rutaEvidencia)
            
                
        except Exception as e:
            if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Invidivual":
                print("[LOG] No se generará Word")
            else:
                crear_tabla_validacion(self.context.xdoc,self.context.iteracion,"FAILED",str(self.context.expected_status_code),str(responseData.status_code))
                guardarWord(self.context.xdoc,self.context.rutaEvidencia)
            print("[LOG] Error al validar el estado del response")
            log_messages += f"\nError al validar el estado del response:{e}"
            self.context.custom_message = log_messages
            raise AssertionError("[LOG] Error al validar el estado del response")

    def validacion_texto_response(self,responseData,datos):
        try:
            self.context.custom_message =""
            validacion=" "
            print("[LOG] Se valida el contenido del response")
            log_messages = ""
            if self.get_data()[int(datos)-1]["Expected Content_1"]:
                log_messages += "\n[LOG] Se valida el contenido del response\n\n"
                if 'json' in responseData.headers.get('Content-Type', ''):
                    actual_content = pretty_print_headers(responseData.json())
                elif 'text/xml' in responseData.headers.get('Content-Type', ''):
                    actual_content = responseData.text
                print(f"Actual Content: {actual_content}")
                log_messages += f"<strong>Actual Content:</strong> {actual_content}\n\n\n" 
                for i in range(1, 7, 1):
                    vString=f"Expected Content_{i}"
                    print(vString)
                    if self.get_data()[int(datos)-1][vString]:
                        self.context.expected_content= self.get_data()[int(datos)-1][vString]
                        print(f"Expected Content: {self.context.expected_content}")
                        log_messages += f"Expected Content {i}: {self.context.expected_content}\n"
                        
                        # Verificar si es una validación de timestamp dinámico
                        if self.context.expected_content.startswith('TIMESTAMP:'):
                            # Validación de timestamp dinámico
                            is_valid, timestamp_log = validate_dynamic_timestamp(
                                self.context.expected_content, 
                                str(actual_content), 
                                self.context
                            )
                            
                            log_messages += f"Validación de timestamp dinámico:\n{timestamp_log}\n"
                            
                            if is_valid:
                                log_messages+="<strong>PASSED</strong>\n\n"
                                validacion+="PASSED "
                                if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Invidivual":
                                    print("[LOG] No se generará Word")
                                else:
                                    crear_tabla_validacion(self.context.xdoc,self.context.iteracion,"TIMESTAMP VALID",str(self.context.expected_content),title="Validación de Timestamp Dinámico")
                                    guardarWord(self.context.xdoc,self.context.rutaEvidencia)
                            else:
                                log_messages+="<strong>FAILED</strong>\n\n"
                                validacion+="FAILED "
                                if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Invidivual":
                                    print("[LOG] No se generará Word")
                                else:
                                    crear_tabla_validacion(self.context.xdoc,self.context.iteracion,"TIMESTAMP INVALID",str(self.context.expected_content),title="Validación de Timestamp Dinámico")
                                    guardarWord(self.context.xdoc,self.context.rutaEvidencia)
                        else:
                            # Validación de contenido regular
                            if self.context.expected_content in pretty_print_headers(responseData.json()):
                                log_messages+="<strong>PASSED</strong>\n\n"
                                validacion+="PASSED "
                                if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Invidivual":
                                    print("[LOG] No se generará Word")
                                else:
                                    crear_tabla_validacion(self.context.xdoc,self.context.iteracion,"FOUND",str(self.context.expected_content),title="Validación de texto del Response")
                                    guardarWord(self.context.xdoc,self.context.rutaEvidencia)
                            else:
                                log_messages+="<strong>FAILED</strong>\n\n"
                                validacion+="FAILED "
                                if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Invidivual":
                                    print("[LOG] No se generará Word")
                                else:
                                    crear_tabla_validacion(self.context.xdoc,self.context.iteracion,"NOT FOUND",str(self.context.expected_content),title="Validación de texto del Response")
                                    guardarWord(self.context.xdoc,self.context.rutaEvidencia)
                    else:
                        break    
                if validacion != " ":
                    print(validacion)
                    assert "FAILED" not in validacion
                    print("[LOG] Se realizo la validación del contenido correctamente!")
            else:
                log_messages="No hay validaciones"                
            
            self.context.custom_message = log_messages
        except Exception as e:
                self.context.custom_message =f"Error al validar el contenido del response:{log_messages}{e}"
                print("[LOG] Error al validar el contenido del response")
                raise AssertionError("[LOG] Error al validar el contenido del response")

    def validacion_header_response(self,reponseData):
        try:
            print("[LOG] Se valida los Headers Response")
            if self.context.expected_headers:
                actual_headers_response = reponseData.headers
 
                # Convertir los encabezados esperados y reales a diccionarios
                expected_headers_dict = json.loads(self.context.expected_headers)
                actual_headers_dict = {k: v for k, v in actual_headers_response.items()}
    
                # Convertir los diccionarios a cadenas formateadas para la comparación
                expected_headers_str = json.dumps(expected_headers_dict, indent=4)
                actual_headers_str = json.dumps(actual_headers_dict, indent=4)
    
                print(f"Expected Headers Response: {expected_headers_str}")
                print(f"Actual Headers Response: {actual_headers_str}")
                log_messages = ""
                log_messages += "[LOG] Se valida los Headers Response\n"
                log_messages += f"Expected Headers Response: {expected_headers_str}\n"
                log_messages += f"Actual Headers Response: {actual_headers_str}\n\n"
                self.context.custom_message = log_messages
                contador=0
                validacion=" "
                # Validar que los encabezados esperados estén en los encabezados reales, omitiendo Content-Length y Date
                for key, value in expected_headers_dict.items():
                    contador+=1
                    log_messages+=f"<strong>Validacion Header {contador}</strong>\n"
                    log_messages+=f"Header Esperado: {key}\n"
                    if key in actual_headers_dict:
                        log_messages+=f'<span style="color: green;"><strong>PASSED</strong></span>'
                        validacion+="PASSED "
                        if value!="*":
                            log_messages+=f"\nValor Esperado: {value}\n"
                            log_messages+=f"Valor Obtenido: {actual_headers_dict[key]}\n"
                            if actual_headers_dict[key]==value:
                                log_messages+=f'<span style="color: green;"><strong>PASSED</strong></span>\n\n'
                                validacion+="PASSED "
                            else:
                                log_messages+=f'<span style="color: red;"><strong>FAILED</strong></span>\n\n'
                                validacion+="FAILED "
                        else:
                            log_messages+="\nSolo se valida la existencia del header\n\n"
                    else:
                        validacion+="FAILED "
                        log_messages+=f'<span style="color: red;"><strong>FAILED</strong></span> - No existe el header en el response\n\n'
                        #assert key in actual_headers_dict and actual_headers_dict[key] == value
                self.context.custom_message = log_messages
                if validacion != " ":
                    print(validacion)
                    assert "FAILED" not in validacion
                    print("[LOG] Se realizo la validación del contenido correctamente!")
                    if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Invidivual":
                        print("[LOG] No se generará Word")
                    else:
                        crear_tabla_validacion_header(self.context.xdoc, expected_headers_str, actual_headers_str, "PASSED")
                        guardarWord(self.context.xdoc, self.context.rutaEvidencia)
            else:
                log_messages="No hay validaciones"
                self.context.custom_message = log_messages
        except Exception as e:
            if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Invidivual":
                print("[LOG] No se generará Word")
            else:
                crear_tabla_validacion_header(self.context.xdoc, expected_headers_str, actual_headers_str, "FAILED")
                guardarWord(self.context.xdoc, self.context.rutaEvidencia)
            print("[LOG] Error al validar los headers del response")
            log_messages += f"\nError al validar los headers del response: {e}"
            self.context.custom_message = log_messages
            raise AssertionError("[LOG] Error al validar los headers del response")
    
    def validacion_estructura_response(self,reponseData):
        try:
            print("[LOG] Se valida la estructura del Response")
            if self.context.expected_response:
                actual_response = reponseData.text
 
                # Convertir los encabezados esperados y reales a diccionarios
                expected_response_dict = json.loads(self.context.expected_response)
                actual_response_dict = json.loads(actual_response)
                # Convertir los diccionarios a cadenas formateadas para la comparación
                # expected_reponse_str = json.dumps(expected_response_dict, indent=4, ensure_ascii=False)
                # actual_response_str = json.dumps(actual_response_dict, indent=4, ensure_ascii=False)
                log_messages = ""
                log_messages += "[LOG] Se valida la estructura del Response\n"
                if (len(str(actual_response_dict))<10000):
                    #log_messages += f"Expected Response: {pretty_print_headers(expected_response_dict)}\n"
                    log_messages += f"Actual Response: {pretty_print_headers(actual_response_dict)}\n\n"
                self.context.custom_message = log_messages
                contador=0
                validacion=" "
                log_messages=""
                validation_results = validate_keys_and_values(self.context,expected_response_dict,actual_response_dict,log=log_messages)
                log_messages = validation_results['log']
                has_failures = validation_results['has_failures']
                self.context.custom_message += log_messages
                
                if has_failures:
                    if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Individual":
                        print("[LOG] No se generará Word")
                    else:
                        crear_tabla_validacion(self.context.xdoc,self.context.iteracion,"FAILED","Estructura del Response","Validación fallida",title="Validación de estructura del Response")
                        guardarWord(self.context.xdoc,self.context.rutaEvidencia)
                    raise AssertionError("[LOG] Validación de estructura del response falló")
                else:
                    print("[LOG] Validación de estructura del response exitosa")
                    if hasattr(self.context,'evidence_path') and self.context.tipoWord!="Individual":
                        print("[LOG] No se generará Word")
                    else:
                        crear_tabla_validacion(self.context.xdoc,self.context.iteracion,"PASSED","Estructura del Response","Validación exitosa",title="Validación de estructura del Response")
                        guardarWord(self.context.xdoc,self.context.rutaEvidencia)
            else:
                log_messages="No hay validaciones"
        except Exception as e:
            print(f"[LOG] Error al validar la estructura del response: {e}")
            # Crear log de error detallado
            error_log = f"\nError al validar la estructura del response: {e}\n"
            
            # Intentar mostrar diferencias si es posible
            try:
                if hasattr(self.context, 'expected_response') and hasattr(self.context, 'response'):
                    differences = highlight_differences(self.context.expected_response, pretty_print_headers(self.context.response.json()))
                    error_log += f"Differences:\n{differences}\n"
            except:
                error_log += "No se pudieron mostrar las diferencias\n"
            
            # Agregar el log de error al mensaje personalizado
            if hasattr(self.context, 'custom_message'):
                self.context.custom_message += error_log
            else:
                self.context.custom_message = error_log
            
            # Crear documentación del error si es necesario
            if hasattr(self.context, 'evidence_path') and self.context.tipoWord != "Individual":
                print("[LOG] No se generará Word")
            else:
                try:
                    crear_tabla_validacion(self.context.xdoc, self.context.iteracion, "ERROR", "Estructura del Response", str(e), title="Error en validación de estructura")
                    guardarWord(self.context.xdoc, self.context.rutaEvidencia)
                except:
                    print("[LOG] No se pudo generar documentación del error")
            
            raise AssertionError(f"[LOG] Error al validar la estructura del response: {e}")


def validate_keys_and_values(context, expected, actual, parent_key='', log=''):
    """
    Valida llaves y valores de un diccionario esperado contra uno actual.
    Retorna un diccionario con los resultados de la validación.
    """
    has_failures = False
    
    for key in expected:
        log += f"\nLlave esperada: {str(key)}\n"
        full_key = f"{parent_key}.{key}" if parent_key else key
        
        if key in actual:
            log += f'<span style="color: green;"><strong>PASSED</strong></span>\n'
            if hasattr(context, 'evidence_path') and context.tipoWord != "Individual":
                print("[LOG] No se generará Word")
            else:
                crear_tabla_validacion(context.xdoc, context.iteracion, "FOUND", str(key), title="Llaves")
                guardarWord(context.xdoc, context.rutaEvidencia)
            
            if isinstance(expected[key], dict):
                # Validación recursiva para diccionarios anidados
                nested_result = validate_keys_and_values(context, expected[key], actual[key], full_key, log='')
                log += nested_result['log']
                if nested_result['has_failures']:
                    has_failures = True
            elif isinstance(expected[key], list) and isinstance(actual[key], list):
                # Validar listas de diccionarios
                for i, item in enumerate(expected[key]):
                    if isinstance(item, dict):
                        nested_result = validate_keys_and_values(context, item, actual[key][i], f"{full_key}[{i}]", log='')
                        log += nested_result['log']
                        if nested_result['has_failures']:
                            has_failures = True
            else:
                if expected[key] != "*":
                    log += f"Valor esperado: {str(expected[key])}\n"
                    log += f"Valor Obtenido: {str(actual[key])}\n"
                    
                    # Verificar si es una validación de timestamp dinámico
                    if str(expected[key]).startswith('TIMESTAMP:'):
                        try:
                            is_valid, timestamp_log = validate_dynamic_timestamp(
                                str(expected[key]), 
                                str(actual[key]), 
                                context
                            )
                            
                            log += f"Validación de timestamp dinámico:\n{timestamp_log}\n"
                            
                            if is_valid:
                                log += f'<span style="color: green;"><strong>PASSED</strong></span>\n'
                                if hasattr(context, 'evidence_path') and context.tipoWord != "Individual":
                                    print("[LOG] No se generará Word")
                                else:
                                    crear_tabla_validacion(context.xdoc, context.iteracion, "TIMESTAMP VALID", str(expected[key]), str(actual[key]), title="Timestamp Dinámico")
                                    guardarWord(context.xdoc, context.rutaEvidencia)
                            else:
                                log += f'<span style="color: red;"><strong>FAILED</strong></span>\n'
                                has_failures = True
                                if hasattr(context, 'evidence_path') and context.tipoWord != "Individual":
                                    print("[LOG] No se generará Word")
                                else:
                                    crear_tabla_validacion(context.xdoc, context.iteracion, "TIMESTAMP INVALID", str(expected[key]), str(actual[key]), title="Timestamp Dinámico")
                                    guardarWord(context.xdoc, context.rutaEvidencia)
                        except Exception as e:
                            log += f'<span style="color: red;"><strong>ERROR</strong></span> - Error en validación de timestamp: {str(e)}\n'
                            has_failures = True
                    else:
                        # Validación de valor regular
                        if expected[key] == actual[key]:
                            log += f'<span style="color: green;"><strong>PASSED</strong></span>\n'
                            if hasattr(context, 'evidence_path') and context.tipoWord != "Individual":
                                print("[LOG] No se generará Word")
                            else:
                                crear_tabla_validacion(context.xdoc, context.iteracion, "PASSED", str(expected[key]), str(actual[key]), title="Valor")
                                guardarWord(context.xdoc, context.rutaEvidencia)
                        else:
                            log += f'<span style="color: red;"><strong>FAILED</strong></span>\n'
                            has_failures = True
                            if hasattr(context, 'evidence_path') and context.tipoWord != "Individual":
                                print("[LOG] No se generará Word")
                            else:
                                crear_tabla_validacion(context.xdoc, context.iteracion, "FAILED", str(expected[key]), str(actual[key]), title="Valor")
                                guardarWord(context.xdoc, context.rutaEvidencia)
                else:
                    log += "Solo se valida la existencia de la llave\n\n"
        else:
            log += f'<span style="color: red;"><strong>FAILED</strong></span> - No existe la llave en el response\n\n'
            has_failures = True
            if hasattr(context, 'evidence_path') and context.tipoWord != "Individual":
                print("[LOG] No se generará Word")
            else:
                crear_tabla_validacion(context.xdoc, context.iteracion, "NOT FOUND", str(key), title="Llaves")
                guardarWord(context.xdoc, context.rutaEvidencia)
            print(f"Clave faltante en actual_response: {full_key}")
    
    return {
        'log': log,
        'has_failures': has_failures
    }