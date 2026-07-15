import http.server
import socketserver
import json
import pandas as pd
import numpy as np
import re
import os

PORT = 8000
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "..", "Dataset_Clinico_Crudo_Errores.xlsx")

def get_clean_data():
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="Datos Cl\u00ednicos Crudos")
        
        # 1. Estandarizar 'Tramo Edad'
        def clean_edad(val):
            if pd.isna(val): return np.nan
            val = str(val).lower().strip()
            if 'jov' in val: return 'Joven'
            elif 'adul' in val: return 'Adulto'
            elif 'sen' in val: return 'Senior'
            return np.nan
        df['Tramo Edad'] = df['Tramo Edad'].apply(clean_edad)
        
        # 2. Estandarizar 'Tipo Prueba'
        def clean_prueba(val):
            if pd.isna(val): return np.nan
            val = str(val).lower().strip()
            if 'mam' in val: return 'Mamograf\u00eda'
            elif 'rmn' in val or 'reso' in val: return 'RMN'
            elif 'tac' in val or 'tom' in val: return 'TAC'
            return np.nan
        df['Tipo Prueba'] = df['Tipo Prueba'].apply(clean_prueba)
        
        # 3. Tratar nulos e incoherencias
        for col in ['Total Pruebas', 'Aciertos IA', 'Aciertos M\u00e9dicos']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan
            
        df.dropna(subset=['Tramo Edad', 'Tipo Prueba', 'Aciertos IA', 'Aciertos M\u00e9dicos'], inplace=True)
        
        # 4. Eliminar duplicados
        def clean_id(val):
            if pd.isna(val): return np.nan
            val = str(val).strip().upper()
            nums = re.findall(r'\d+', val)
            if nums:
                return f"LOTE-{int(nums[0]):03d}"
            return np.nan
        df['ID Lote'] = df['ID Lote'].apply(clean_id)
        df.dropna(subset=['ID Lote'], inplace=True)
        # df.drop_duplicates(subset=['ID Lote'], keep='first', inplace=True)
        
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error processing data: {e}")
        return []

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/data.json'):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            data = get_clean_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
