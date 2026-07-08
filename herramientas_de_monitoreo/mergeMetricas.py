import pandas as pd
import os
import argparse
from pathlib import Path
from datetime import datetime
import re


def mergear_csv(path, mango, psutil):

    archivo = os.path.join(
        path,
        f"{Path(psutil).stem}_merge.csv"
    )

    # Cargar datos
    df_psutil = pd.read_csv(psutil)
    
    df_mango = pd.read_csv(mango)

    if "elapsed" not in df_mango.columns:
        df_mango = pd.read_csv(mango, skiprows=2)
        df_mango["elapsed"] = df_mango["elapsed"] / 1e9  

    # correccion de desfase

    fecha_mango = extraer_timestamp(Path(mango))
    fecha_psutil = extraer_timestamp(Path(psutil))

    offset = (fecha_psutil - fecha_mango).total_seconds()

    df_psutil["elapsed"] += offset

    #Se eliminan filas con tiempo negativo
    df_psutil = df_psutil[df_psutil["elapsed"] >= 0]

    # Seleccionar SOLO las columnas que necesito de df_mango
    df_mango_subset = df_mango[["elapsed", "fps", "frametime"]]

    # Ordenar ambos (necesario para merge_asof)
    df_psutil = df_psutil.sort_values("elapsed")
    df_mango_subset = df_mango_subset.sort_values("elapsed")

    # Realizar merge_asof con tolerancia (opcional)
    df_final = pd.merge_asof(
        df_psutil,
        df_mango_subset,
        on="elapsed",
        direction="nearest",
        tolerance=0.5
    )

    if os.path.exists(archivo):
        os.remove(archivo)

    # Guardar resultado
    df_final.to_csv(archivo, index=False, na_rep="NaN")

def obtener_archivos(path):
    return [archivo for archivo in Path(path).iterdir() if archivo.is_file()]

def extraer_timestamp(nombre):
    fechaStr = re.search(
        r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})",
        nombre.name
    ).group(1)
    

    return datetime.strptime(fechaStr, "%Y-%m-%d_%H-%M-%S")

def extraer_monitor(archives):
    elementos = []

    for i in archives:
        if ("monitor" in i.name):
            elementos.append(i)

    return elementos

def extraer_herramienta(archives):
    elementos = []

    for i in archives:
        if not ("monitor" in i.name):
            elementos.append(i)

    return elementos

def emparejar_archivos(mangohud, monitor):

    elementos = []
    
    for herr in mangohud:

        toSafe = None
        mejor_diferencia = None

        fecha_herr = extraer_timestamp(herr)

        for moni in monitor:
            fecha_moni = extraer_timestamp(moni)

            if toSafe is None:
                toSafe = (moni, herr)
                mejor_diferencia = abs(fecha_moni - fecha_herr)
            else:
                diferencia = abs(fecha_moni - fecha_herr)

                if diferencia < mejor_diferencia:
                    mejor_diferencia = diferencia
                    toSafe = (moni, herr)
            
        elementos.append(toSafe)
        monitor.remove(toSafe[0])
    
    return elementos

parser = argparse.ArgumentParser()

parser.add_argument("--pathGet", required=True)

parser.add_argument("--pathSafe", required=True)

args = parser.parse_args()

os.makedirs(args.pathSafe, exist_ok=True)

nombres = obtener_archivos(args.pathGet)

coupleArch = emparejar_archivos(extraer_herramienta(nombres), extraer_monitor(nombres))

for psutil, mangohud in coupleArch:
    mergear_csv(args.pathSafe, mangohud, psutil)
