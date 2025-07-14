from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureNamedKeyCredential
from azure.keyvault.secrets import SecretClient
from azure.data.tables import TableServiceClient
from azure.data.tables import TableEntity
from src.test.library.variables import *
from azure.core.pipeline.transport import RequestsTransport
import requests

def get_key_secrets():
    account_name = 'pocstoragemibanco'
    key_vault_name = 'key-db-auto'
    table_name = 'LogsTable'
    secret_storage_account_key = 'secret-storage-account-key'
    
    KVUri = f"https://{key_vault_name}.vault.azure.net"
    credential = DefaultAzureCredential()
    print(f"Key Vault URI: {KVUri}")
    client = SecretClient(vault_url=KVUri, credential=credential)

    retrieved_account_key = client.get_secret(secret_storage_account_key)

    return account_name, retrieved_account_key.value, table_name

def get_table_client():
    #account_name, account_key, table_name = get_key_secrets()
    
    try:
        # Crear el objeto de credencial
        credential = AzureNamedKeyCredential(name=account_name, key=account_key)
        
        ##DESHABILITAR SSL
        session = requests.Session()
        session.verify = False
        transport = RequestsTransport(session=session)

        # Crear el cliente de servicio de tabla
        service_client = TableServiceClient(
            endpoint=f"https://{account_name}.table.core.windows.net",
            credential=credential,
            transport=transport
        )

        # Obtener el cliente de tabla
        table_client = service_client.get_table_client(table_name=table_name)
        print("Connection to Azure Table Storage established")
    except Exception as e:
        print(f"Error creating table client: {e}")
        raise

    return table_client

def save_to_table(context, scenario):
    try:
        table_client = context.table_client
        scenario_name = context.nameEscenario # Diferente a web
        fecha = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M:%S")
        framework = "Servicios"
        hostname = context.hostname
        partition_key = "TestResults"
        row_key = str(datetime.now().timestamp()).replace('.', '')

        # Datos a guardar en la tabla
        row_data = TableEntity()
        row_data['PartitionKey'] = partition_key
        row_data['RowKey'] = row_key
        row_data['Escenario'] = scenario_name
        row_data['Fecha'] = fecha
        row_data['Hora'] = hora
        row_data['Duracion'] = context.timer.total_seconds()
        row_data['Estado'] = context.estado
        row_data['Framework'] = framework
        row_data['Hostname'] = hostname
        row_data['Proyecto'] = context.proyecto

        print(f"Row data to insert: {row_data}")

        # Insertar los datos en la tabla
        table_client.create_entity(entity=row_data)
        print("Data inserted successfully")
    except Exception as e:
        print(f"Error al conectar o ejecutar la consulta en la base de datos: {e}")
        raise