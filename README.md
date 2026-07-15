# Dashboard-datos-cl-nicos

Dashboard interactivo y servidor dinámico en Python para visualizar y analizar en tiempo real datos clínicos sobre la precisión diagnóstica de Inteligencia Artificial frente a Médicos.

## Funcionalidades
- **Servidor Dinámico (Python)**: Lee y limpia un archivo Excel (`Dataset_Clinico_Crudo_Errores.xlsx`) bajo demanda y provee los datos limpios mediante una API JSON.
- **Limpieza de Datos**: Tratamiento automático de valores atípicos, estandarización de columnas y control de inconsistencias.
- **Dashboard Frontend (HTML/JS/CSS)**: Pantalla de control web premium, interactiva y con "Dark Mode" para visualizar KPIs y gráficos utilizando Chart.js.
- **Actualización en Tiempo Real**: Sincronización automática de gráficos y estadísticas al modificar la base de datos Excel original sin necesidad de recargar la página.

## Cómo ejecutar localmente
1. Abre una terminal y colócate en la carpeta `Dashboard`.
2. Ejecuta el servidor Python: `python server.py`
3. Abre el navegador en `http://localhost:8000`
