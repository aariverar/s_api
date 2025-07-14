import datetime
import re
import json
from typing import Dict, Any, Union

class TimestampValidator:
    """
    Clase para validar timestamps dinámicos en respuestas de APIs
    """
    
    def __init__(self):
        self.timestamp_patterns = {
            # Formato ISO 8601 completo
            'iso_full': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$',
            # Formato ISO 8601 con timezone
            'iso_tz': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?[+-]\d{2}:\d{2}$',
            # Formato Unix timestamp (segundos)
            'unix_seconds': r'^\d{10}$',
            # Formato Unix timestamp (milisegundos)
            'unix_milliseconds': r'^\d{13}$',
            # Formato fecha simple YYYY-MM-DD
            'date_simple': r'^\d{4}-\d{2}-\d{2}$',
            # Formato fecha con hora YYYY-MM-DD HH:MM:SS
            'datetime_simple': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
            # Formato personalizado para APIs específicas
            'custom': r''  # Se puede definir según necesidades
        }
    
    def validate_timestamp_format(self, timestamp_value: str, format_type: str) -> bool:
        """
        Valida si un timestamp tiene el formato especificado
        
        Args:
            timestamp_value: El valor del timestamp a validar
            format_type: Tipo de formato a validar ('iso_full', 'unix_seconds', etc.)
            
        Returns:
            bool: True si el formato es válido, False en caso contrario
        """
        if format_type not in self.timestamp_patterns:
            return False
            
        pattern = self.timestamp_patterns[format_type]
        if not pattern:  # Para formato custom vacío
            return True
            
        return bool(re.match(pattern, str(timestamp_value)))
    
    def validate_timestamp_range(self, timestamp_value: str, 
                                format_type: str, 
                                min_time: datetime.datetime = None,
                                max_time: datetime.datetime = None) -> bool:
        """
        Valida si un timestamp está dentro de un rango de tiempo específico
        
        Args:
            timestamp_value: El valor del timestamp a validar
            format_type: Tipo de formato del timestamp
            min_time: Tiempo mínimo permitido (opcional)
            max_time: Tiempo máximo permitido (opcional)
            
        Returns:
            bool: True si está en el rango válido, False en caso contrario
        """
        try:
            # Convertir el timestamp a datetime
            dt = self._convert_to_datetime(timestamp_value, format_type)
            
            if min_time and dt < min_time:
                return False
            if max_time and dt > max_time:
                return False
                
            return True
        except Exception:
            return False
    
    def validate_timestamp_current(self, timestamp_value: str, 
                                  format_type: str,
                                  tolerance_seconds: int = 300) -> bool:
        """
        Valida si un timestamp es aproximadamente el tiempo actual
        
        Args:
            timestamp_value: El valor del timestamp a validar
            format_type: Tipo de formato del timestamp
            tolerance_seconds: Tolerancia en segundos (default: 5 minutos)
            
        Returns:
            bool: True si el timestamp es actual dentro de la tolerancia
        """
        try:
            timestamp_dt = self._convert_to_datetime(timestamp_value, format_type)
            current_dt = datetime.datetime.now()
            
            # Calcular la diferencia en segundos
            diff = abs((timestamp_dt - current_dt).total_seconds())
            
            return diff <= tolerance_seconds
        except Exception:
            return False
    
    def _convert_to_datetime(self, timestamp_value: str, format_type: str) -> datetime.datetime:
        """
        Convierte un timestamp a objeto datetime según su formato
        
        Args:
            timestamp_value: El valor del timestamp
            format_type: Tipo de formato del timestamp
            
        Returns:
            datetime.datetime: Objeto datetime convertido
        """
        if format_type == 'iso_full':
            # Manejar formato ISO 8601
            timestamp_value = timestamp_value.replace('Z', '+00:00')
            if '.' in timestamp_value:
                return datetime.datetime.fromisoformat(timestamp_value)
            else:
                return datetime.datetime.fromisoformat(timestamp_value + '+00:00')
        
        elif format_type == 'iso_tz':
            return datetime.datetime.fromisoformat(timestamp_value)
        
        elif format_type == 'unix_seconds':
            return datetime.datetime.fromtimestamp(int(timestamp_value))
        
        elif format_type == 'unix_milliseconds':
            return datetime.datetime.fromtimestamp(int(timestamp_value) / 1000)
        
        elif format_type == 'date_simple':
            return datetime.datetime.strptime(timestamp_value, '%Y-%m-%d')
        
        elif format_type == 'datetime_simple':
            return datetime.datetime.strptime(timestamp_value, '%Y-%m-%d %H:%M:%S')
        
        else:
            raise ValueError(f"Formato de timestamp no soportado: {format_type}")
    
    def get_timestamp_info(self, timestamp_value: str, format_type: str) -> Dict[str, Any]:
        """
        Obtiene información detallada sobre un timestamp
        
        Args:
            timestamp_value: El valor del timestamp
            format_type: Tipo de formato del timestamp
            
        Returns:
            Dict con información del timestamp
        """
        try:
            dt = self._convert_to_datetime(timestamp_value, format_type)
            current_dt = datetime.datetime.now()
            
            return {
                'original_value': timestamp_value,
                'format_type': format_type,
                'datetime_object': dt,
                'formatted_string': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'is_valid_format': self.validate_timestamp_format(timestamp_value, format_type),
                'is_current': self.validate_timestamp_current(timestamp_value, format_type),
                'time_difference_seconds': (dt - current_dt).total_seconds(),
                'is_future': dt > current_dt,
                'is_past': dt < current_dt
            }
        except Exception as e:
            return {
                'original_value': timestamp_value,
                'format_type': format_type,
                'error': str(e),
                'is_valid_format': False
            }

def validate_dynamic_timestamp(expected_value: str, actual_value: str, context) -> tuple[bool, str]:
    """
    Función principal para validar timestamps dinámicos basada en configuración del Excel
    
    Args:
        expected_value: Valor esperado del Excel (configuración de validación)
        actual_value: Valor actual del response
        context: Contexto de la prueba
        
    Returns:
        tuple: (es_valido, mensaje_log)
    """
    validator = TimestampValidator()
    
    # Parsear la configuración del Excel
    # Formato esperado: "TIMESTAMP:formato:validacion"
    # Ejemplo: "TIMESTAMP:iso_full:current"
    # Ejemplo: "TIMESTAMP:unix_seconds:range:2024-01-01,2024-12-31"
    
    if not expected_value.startswith('TIMESTAMP:'):
        return False, f"Configuración de timestamp inválida: {expected_value}"
    
    try:
        parts = expected_value.split(':')
        if len(parts) < 3:
            return False, f"Formato de configuración incompleto: {expected_value}"
        
        format_type = parts[1]
        validation_type = parts[2]
        
        log_message = f"Validando timestamp dinámico:\n"
        log_message += f"Valor actual: {actual_value}\n"
        log_message += f"Formato esperado: {format_type}\n"
        log_message += f"Tipo de validación: {validation_type}\n"
        
        # Validar formato
        if not validator.validate_timestamp_format(actual_value, format_type):
            return False, f"{log_message}ERROR: Formato de timestamp inválido"
        
        log_message += "Formato válido ✓\n"
        
        # Validar según el tipo de validación
        if validation_type == 'current':
            # Validar que sea tiempo actual (con tolerancia)
            tolerance = 300  # 5 minutos por defecto
            if len(parts) > 3:
                tolerance = int(parts[3])
            
            if validator.validate_timestamp_current(actual_value, format_type, tolerance):
                log_message += f"Timestamp actual válido (tolerancia: {tolerance}s) ✓"
                return True, log_message
            else:
                return False, f"{log_message}ERROR: Timestamp no corresponde al tiempo actual"
        
        elif validation_type == 'range':
            # Validar que esté en un rango específico
            if len(parts) < 4:
                return False, f"{log_message}ERROR: Falta definir el rango de fechas"
            
            range_dates = parts[3].split(',')
            if len(range_dates) != 2:
                return False, f"{log_message}ERROR: Formato de rango inválido"
            
            min_date = datetime.datetime.strptime(range_dates[0], '%Y-%m-%d')
            max_date = datetime.datetime.strptime(range_dates[1], '%Y-%m-%d')
            
            if validator.validate_timestamp_range(actual_value, format_type, min_date, max_date):
                log_message += f"Timestamp en rango válido ({range_dates[0]} - {range_dates[1]}) ✓"
                return True, log_message
            else:
                return False, f"{log_message}ERROR: Timestamp fuera del rango permitido"
        
        elif validation_type == 'future':
            # Validar que sea tiempo futuro
            timestamp_dt = validator._convert_to_datetime(actual_value, format_type)
            if timestamp_dt > datetime.datetime.now():
                log_message += "Timestamp futuro válido ✓"
                return True, log_message
            else:
                return False, f"{log_message}ERROR: Timestamp no es tiempo futuro"
        
        elif validation_type == 'past':
            # Validar que sea tiempo pasado
            timestamp_dt = validator._convert_to_datetime(actual_value, format_type)
            if timestamp_dt < datetime.datetime.now():
                log_message += "Timestamp pasado válido ✓"
                return True, log_message
            else:
                return False, f"{log_message}ERROR: Timestamp no es tiempo pasado"
        
        elif validation_type == 'format_only':
            # Solo validar formato
            log_message += "Validación solo de formato ✓"
            return True, log_message
        
        else:
            return False, f"{log_message}ERROR: Tipo de validación no soportado: {validation_type}"
    
    except Exception as e:
        return False, f"Error al validar timestamp dinámico: {str(e)}"
