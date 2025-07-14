import os
import openpyxl

def data(ruta_relativa_excel, nombre_hoja):
    mydata = []

    try:
        ruta = os.path.join(os.getcwd(), "src", "test", "resources","data","excel", ruta_relativa_excel)
        if not os.path.exists(ruta):
            raise Exception(f"El archivo {ruta_relativa_excel} no existe!")

        workbook = openpyxl.load_workbook(ruta)
        sheet = workbook[nombre_hoja]

        header_row = sheet[1]

        for row in sheet.iter_rows(min_row=2, values_only=True):
            current_hash = {}

            for idx, cell in enumerate(row):
                header_cell_value = header_row[idx].value if header_row[idx].value else ""
                cell_value = str(cell) if cell else ""

                current_hash[header_cell_value.strip()] = cell_value.strip()

            mydata.append(current_hash)

    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo excel: {e}")
        raise e

    return mydata