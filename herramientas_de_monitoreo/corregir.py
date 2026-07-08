import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import re


def convertir_nombre(nombre):

    patron = r"(\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2})"

    match = re.search(patron, nombre)

    if match is None:
        return nombre

    fecha = datetime.strptime(
        match.group(1),
        "%m-%d-%Y_%H-%M-%S"
    )

    fecha_nueva = fecha.strftime("%Y-%m-%d_%H-%M-%S")

    return nombre.replace(match.group(1), fecha_nueva)


def estandarizar_csv(archivo):

    print(f"Procesando: {archivo.name}")

    try:
        df = pd.read_csv(archivo)

    except Exception as e:
        print(f"  No se pudo leer: {e}")
        return

    # Corregir nombre de la columna
    if "elapse" in df.columns:
        df.rename(columns={"elapse": "elapsed"}, inplace=True)
        print("  Columna 'elapse' -> 'elapsed'")

    df.to_csv(archivo, index=False)

    nuevo_nombre = convertir_nombre(archivo.name)

    if nuevo_nombre != archivo.name:
        archivo.rename(archivo.with_name(nuevo_nombre))
        print(f"  Archivo renombrado a: {nuevo_nombre}")


parser = argparse.ArgumentParser()

parser.add_argument(
    "--path",
    required=True
)

args = parser.parse_args()

carpeta = Path(args.path)

if not carpeta.exists():
    print("La carpeta no existe.")
    exit()

archivos = sorted(carpeta.glob("*.csv"))

if len(archivos) == 0:
    print("No se encontraron archivos CSV.")
    exit()

for archivo in archivos:
    estandarizar_csv(archivo)

print("Proceso finalizado.")
