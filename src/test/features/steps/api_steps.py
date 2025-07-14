import requests
from behave import given, when, then
from src.test.library.excel_reader import data
import json
import urllib3
from src.test.library.word_generate import *
from src.test.library.utils import *
from src.test.library.util_api import UTIL_API
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import re

@given('se extrae los datos del servicio del excel "{datos}"')
def step_given_api_endpoint(context,datos):
    excel_value = get_tag_value(context.tags, "xc-")
    hoja_value = get_tag_value(context.tags, "pg-")
    context.excel = (excel_value if excel_value is not None else "test_data") + ".xlsx"
    context.hoja = hoja_value if hoja_value is not None else "Hoja1"
    # context.excel="test_data.xlsx"
    # context.hoja="Hoja1"
    context.utilapi= UTIL_API(context)
    context.ejecutar =context.utilapi.get_ejecucion(datos)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    context.custom_message ="-"
    if context.ejecutar=="SI":
        context.state=None
        context.utilapi.lectura_excel(datos)
    else:
        context.state="NO-EXECUTED"
        context.custom_message = "NO-EXECUTED"     
      

@when('cuando envio una peticion al servicio "{datos}"')
def step_when_send_request(context,datos):
    context.utilapi = UTIL_API(context)
    context.custom_message = "-"
    if context.ejecutar == "SI":
        try:
            print('[DEBUG] Entrando a step_when_send_request')
            context.response = context.utilapi.enviar_peticion()
            print('[DEBUG] Respuesta recibida:', context.response)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"[ERROR] Excepción en step_when_send_request: {e}\n{tb}")
            context.state = "FAILED"
            context.custom_message = f"ERROR: {e}\n{tb}"
            # Forzar el fallo del step para que Behave lo registre y continúe
            assert False, f"Error en la petición: {e}\n{tb}"
    else:
        context.state = "NO-EXECUTED"
        context.custom_message = "NO-EXECUTED"

@then('se valida el status code obtenido con el status code esperado "{datos}"')
def step_then_response_status_code(context,datos):
    context.custom_message ="-"
    context.utilapi= UTIL_API(context)
    if context.ejecutar=="SI":
        try:
            context.utilapi.validacion_status_code(context.response)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"[ERROR] Excepción en step_then_response_status_code: {e}\n{tb}")
            context.state = "FAILED"
            context.custom_message = f"ERROR: {e}\n{tb}"
            assert False, f"Error en validación status code: {e}\n{tb}"
    else:
        context.state="NO-EXECUTED"
        context.custom_message = "NO-EXECUTED"

@then('se valida el response obtenido con el response esperado "{datos}"')
def step_then_response_contains_expected_content(context,datos):
    context.custom_message ="-"
    context.utilapi= UTIL_API(context)
    if context.ejecutar=="SI":
        try:
            context.utilapi.validacion_texto_response(context.response,datos)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"[ERROR] Excepción en step_then_response_contains_expected_content: {e}\n{tb}")
            context.state = "FAILED"
            context.custom_message = f"ERROR: {e}\n{tb}"
            assert False, f"Error en validación texto response: {e}\n{tb}"
    else:
        context.state="NO-EXECUTED"
        context.custom_message = "NO-EXECUTED"


    
@then('se valida los headers del response obtenido con los headers esperados "{datos}"')
def step_then_response_contains_expected_content(context,datos):
    context.custom_message ="-"
    context.utilapi= UTIL_API(context)
    if context.ejecutar=="SI":
        try:
            context.utilapi.validacion_header_response(context.response)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"[ERROR] Excepción en step_then_response_contains_expected_content (headers): {e}\n{tb}")
            context.state = "FAILED"
            context.custom_message = f"ERROR: {e}\n{tb}"
            assert False, f"Error en validación headers response: {e}\n{tb}"
    else:
        context.state="NO-EXECUTED"
        context.custom_message = "NO-EXECUTED"

@then('se valida la estructura del response obtenido con el response esperado "{datos}"')
def step_then_response_contains_expected_content(context,datos):
    context.custom_message ="-"
    context.utilapi= UTIL_API(context)
    if context.ejecutar=="SI":
        try:
            context.utilapi.validacion_estructura_response(context.response)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"[ERROR] Excepción en step_then_response_contains_expected_content (estructura): {e}\n{tb}")
            context.state = "FAILED"
            context.custom_message = f"ERROR: {e}\n{tb}"
            assert False, f"Error en validación estructura response: {e}\n{tb}"
    else:
        context.state="NO-EXECUTED"
        context.custom_message = "NO-EXECUTED"