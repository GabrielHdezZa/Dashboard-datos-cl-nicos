import json
import os
import re
import sys
import numpy as np
import pandas as pd
from http.server import BaseHTTPRequestHandler

# Path to the Excel file (relative to project root)
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "..", "Dataset_Clinico_Crudo_Errores.xlsx")

def get_clean_data():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Datos Clínicos Crudos")

    def clean_edad(val):
        if pd.isna(val): return np.nan
        val = str(val).lower().strip()
        if 'jov' in val: return 'Joven'
        elif 'adul' in val: return 'Adulto'
        elif 'sen' in val: return 'Senior'
        return np.nan

    def clean_prueba(val):
        if pd.isna(val): return np.nan
        val = str(val).lower().strip()
        if 'mam' in val: return 'Mamografía'
        elif 'rmn' in val or 'reso' in val: return 'RMN'
        elif 'tac' in val or 'tom' in val: return 'TAC'
        return np.nan

    df['Tramo Edad'] = df['Tramo Edad'].apply(clean_edad)
    df['Tipo Prueba'] = df['Tipo Prueba'].apply(clean_prueba)

    for col in ['Total Pruebas', 'Aciertos IA', 'Aciertos Médicos']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan

    df.dropna(subset=['Tramo Edad', 'Tipo Prueba', 'Aciertos IA', 'Aciertos Médicos'], inplace=True)

    def clean_id(val):
        if pd.isna(val): return np.nan
        val = str(val).strip().upper()
        nums = re.findall(r'\d+', val)
        if nums:
            return f"LOTE-{int(nums[0]):03d}"
        return np.nan

    df['ID Lote'] = df['ID Lote'].apply(clean_id)
    df.dropna(subset=['ID Lote'], inplace=True)

    return df.to_dict(orient='records')


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = get_clean_data()
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            error = json.dumps({"error": str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(error)
