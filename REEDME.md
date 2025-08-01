
# QA API Automation Framework
## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Recomendado: entorno virtual (venv)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/aariverar/s_api.git
   cd s_api
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```


## Descripción General

Framework para automatización de pruebas de APIs REST utilizando Python, Behave y Behavex, con generación robusta de evidencias Word y reportes HTML. Soporta ejecución secuencial y paralela, manejo avanzado de errores, y limpieza automática de artefactos.

---

src/
  test/
    app/           # Lógica de la aplicación y utilidades
    features/      # Features Gherkin, steps y hooks
    library/       # Librerías utilitarias, generación de reportes y evidencias
    reports/       # Reportes HTML y evidencias generadas
    resources/     # Plantillas, datos de prueba, drivers

## Estructura del Proyecto

```
src/
  test/
    app/           # Lógica de la aplicación y utilidades
    features/      # Features Gherkin, steps y hooks
    library/       # Librerías utilitarias, generación de reportes y evidencias
    reports/       # Reportes HTML y evidencias generadas
    resources/     # Plantillas, datos de prueba, drivers
```

## Ejemplo de Feature y Step

**Feature (src/test/features/api_test.feature):**
```gherkin
Feature: Prueba de API
  Scenario: Validar respuesta exitosa
    Given se extrae los datos del servicio del excel "1"
    When cuando envio una peticion al servicio "1"
    Then se valida el status code obtenido con el status code esperado "1"
```

**Step (src/test/features/steps/api_steps.py):**
```python
from behave import given, when, then

@given('se extrae los datos del servicio del excel "{datos}"')
def step_given(context, datos):
    # Implementación aquí
    pass
```

## Integración Continua

Este framework está preparado para integrarse con Azure Pipelines. Consulta el archivo `azure-pipelines.yml` para detalles de configuración y despliegue automático.

## Contribuciones

¿Quieres mejorar el framework? ¡Bienvenido! Por favor:
- Crea un fork y una rama para tu mejora.
- Haz pull requests descriptivos.
- Sigue las convenciones de código y agrega comentarios donde sea necesario.
- Reporta bugs o solicita features usando Issues.

## Licencia

Este proyecto es privado y de uso exclusivo para el equipo de QA de SCB. No distribuir sin autorización.


---

## Ejecución Recomendada

### 1. Limpieza previa

Antes de cada ejecución, limpia artefactos previos:

<!--- bash
python limpieza.py
-->

Esto elimina temporales, caché y evidencias antiguas de forma segura.

### 2. Ejecución secuencial (Behave)


<!--- bash
python limpieza.py && python run_Test.py @TuTag
-->

O también puedes ejecutar simplemente:
```bash
python limpieza.py && python run_Test.py
```
El script te pedirá el tag a ejecutar (por defecto @Santander).

### 3. Ejecución paralela (Behavex)

<!--- bash
python limpieza.py && behavex src/test/features -t=@TuTag --parallel-processes=3
-->

---

## Evidencias y Reportes

- **Evidencias Word:**
  - Cada escenario/proceso genera un archivo `.docx` único (nombre de API, PID, iteración, UUID).
  - Garantiza que en ejecución secuencial y paralela no hay sobrescritura ni pérdida de información.
  - Todas las validaciones (status, llave, valor, headers, estructura) quedan registradas.
  - Ubicación: `reports/<ejecución>/Evidencias/`.

- **Reporte HTML:**
  - Genera un resumen visual de la ejecución.
  - Ejecuta en `library`:
    <!---  bash
    python reporte_paralelo.py
    -->

---

## Manejo de Errores y Robustez

- **HTTP Requests:**
  - Timeouts robustos y clasificación de errores (timeout, proxy, DNS, firewall, endpoint).
  - Todos los errores se propagan y registran; nunca se silencian.
  - Si hay problemas de red, el framework nunca cuelga: siempre muestra resumen y evidencia.

- **Ejecución paralela:**
  - Evidencias y reportes son únicos por proceso/escenario.
  - No hay sobrescritura ni pérdida de archivos.

- **Limpieza automática:**
  - `limpieza.py` elimina todo rastro de ejecuciones previas.

---

## Recomendaciones de Red (VPN/Proxy)

Si experimentas bloqueos, cuelgues o falta de respuesta en pruebas de API:

- Verifica tu conexión a internet.
- Si usas VPN o proxy, podrían bloquear conexiones HTTP/HTTPS salientes.
- Prueba desconectando la VPN o consulta con IT para configurar el acceso desde Python.

---

## Buenas Prácticas

- Ejecuta siempre `limpieza.py` antes de cada suite.
- Usa tags para filtrar escenarios relevantes.
- Revisa los archivos `.docx` y el HTML generado tras cada ejecución.
- Ante errores de red, consulta el log y la evidencia Word para diagnóstico.

---

## Créditos y Contacto

Desarrollado y mantenido por Abraham Rivera Rivadeneyra (SCB).
Para soporte, contacta a tu líder técnico o al área de QA.