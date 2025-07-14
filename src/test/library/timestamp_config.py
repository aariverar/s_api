# Configuración de Validación de Timestamps
# Este archivo permite personalizar los formatos y validaciones de timestamps

# Formatos de timestamp personalizados
CUSTOM_TIMESTAMP_FORMATS = {
    # Formato personalizado para API de MiBanco
    'mibanco_datetime': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$',
    
    # Formato personalizado para timestamps con microsegundos
    'iso_microseconds': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z?$',
    
    # Formato personalizado para fechas en español
    'spanish_date': r'^\d{2}/\d{2}/\d{4}$',
    
    # Formato personalizado para hora 24h
    'time_24h': r'^\d{2}:\d{2}:\d{2}$',
    
    # Formato personalizado para timestamps de bases de datos
    'db_timestamp': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$'
}

# Configuraciones de tolerancia por defecto
DEFAULT_TOLERANCES = {
    'current': 300,      # 5 minutos
    'current_strict': 60,  # 1 minuto
    'current_loose': 1800, # 30 minutos
}

# Configuraciones de validación especiales
SPECIAL_VALIDATIONS = {
    # Validación para horario de trabajo (9 AM - 6 PM)
    'business_hours': {
        'start_hour': 9,
        'end_hour': 18,
        'weekdays_only': True
    },
    
    # Validación para fechas de vencimiento (futuro pero no muy lejano)
    'expiry_date': {
        'min_days_future': 1,
        'max_days_future': 365
    },
    
    # Validación para logs de auditoría (pasado pero no muy antiguo)
    'audit_log': {
        'max_days_past': 90
    }
}

# Mensajes de error personalizados
ERROR_MESSAGES = {
    'es': {
        'invalid_format': 'Formato de timestamp inválido',
        'not_current': 'El timestamp no corresponde al tiempo actual',
        'out_of_range': 'Timestamp fuera del rango permitido',
        'not_future': 'El timestamp no es tiempo futuro',
        'not_past': 'El timestamp no es tiempo pasado',
        'business_hours': 'El timestamp no está en horario de trabajo',
        'expiry_invalid': 'Fecha de vencimiento inválida'
    },
    'en': {
        'invalid_format': 'Invalid timestamp format',
        'not_current': 'Timestamp does not correspond to current time',
        'out_of_range': 'Timestamp out of allowed range',
        'not_future': 'Timestamp is not future time',
        'not_past': 'Timestamp is not past time',
        'business_hours': 'Timestamp is not in business hours',
        'expiry_invalid': 'Invalid expiry date'
    }
}

# Configuraciones por ambiente
ENVIRONMENT_CONFIGS = {
    'development': {
        'tolerance_multiplier': 2,  # Tolerancia más alta en desarrollo
        'strict_validation': False
    },
    'staging': {
        'tolerance_multiplier': 1.5,
        'strict_validation': False
    },
    'production': {
        'tolerance_multiplier': 1,
        'strict_validation': True
    }
}

# Configuraciones por tipo de API
API_TYPE_CONFIGS = {
    'authentication': {
        'default_tolerance': 60,
        'validate_future_tokens': True
    },
    'audit': {
        'default_tolerance': 300,
        'validate_past_only': True
    },
    'scheduling': {
        'default_tolerance': 1800,
        'validate_future_required': True
    }
}
