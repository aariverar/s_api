import os

# Usar os.path.join para construir las rutas de manera que sean compatibles con cualquier sistema operativo
html_features_template = os.path.join(os.getcwd(), "src", "test", "resources", "template", "overview-features.html")
html_for_each_feature_template = os.path.join(os.getcwd(), "src", "test", "resources", "template", "report-feature.html")
report_folder_path = os.path.join(os.getcwd(), "src", "test", "reports")
template_folder_path = os.path.join(os.getcwd(), "src", "test", "resources", "template")
source_files = ["logo_mibanco.png", "main.js", "style.css", "icon.ico"]
word_path1 = os.path.join(os.getcwd(), "Evidencias")


# Variables que se usan para conectarse a Azure portal
account_name = '' #storage account name
key_vault_name = '' #key vault name
table_name = '' #table name in storage table service
secret_storage_account_key = '' #secret name in key vault

account_key=''
   