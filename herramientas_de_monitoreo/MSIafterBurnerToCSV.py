import pandas as pd
import argparse
from datetime import datetime
import re
import time
import psutil
import numpy as np
import subprocess
import os
from pathlib import Path

def get_process(name_process, timeout=None):
    start = time.time()
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if name_process.lower() in proc.info['name'].lower():
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if timeout and (time.time() - start) > timeout:
            raise TimeoutError(f"Proceso {name_process} no encontrado después de {timeout}s")
        time.sleep(0.5) 

def extraer_timestamp(fecha):
    return datetime.strptime(fecha,  "%d-%m-%Y %H:%M:%S")

def close_rtss():
    for name in ("RTSS.exe", "RTSSHooksLoader.exe", "RTSSHooksLoader64.exe"):
        for p in psutil.process_iter(["name"]):
            try:
                if p.info["name"] == name:
                    print(f"Cerrando {name}")
                    p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

def createLogCSV(archive, process, pathSafe):


    df = pd.read_csv(
        archive,
        skiprows=2,          # salta las líneas 00 y 01
        header=0,            # la línea 02 contiene los nombres
        sep=",",
        encoding="cp1252",
        skipinitialspace=True
    )

    # Limpiar archivo
    df.columns = df.columns.str.strip()
    df = df.drop(df.columns[0], axis=1)
    df[df.columns[0]] = pd.to_datetime(
        df[df.columns[0]],
        format="%d-%m-%Y %H:%M:%S"
    )

    startime = extraer_timestamp(df.columns[0])

    df["elapsed"] = (df[df.columns[0]]-startime).dt.total_seconds()
    df = df.rename(columns={"Frametime": "frametime"})
    df["frametime"] = pd.to_numeric(df["frametime"], errors="coerce")
    df["fps"] = np.where(
        df["frametime"] > 0,
        (1000 / df["frametime"]).round(2),
        np.nan
    )

    archivo_salida = pathSafe / f"{process}_{startime.strftime('%Y-%m-%d-_%H-%M-%S')}.csv"

    # Guardar CSV
    df.to_csv(
        archivo_salida,
        index=False,
        encoding="utf-8-sig"
    )

    print("Convertido correctamente")
    print(df.head())
    print(df.shape)

def continuous_monitoring(archive, process, pathSafe):
    afterburner = None

    try:
        while True:

            # Obtener el proceso

            print(f"Esperando el proceso '{process}'...")

            process_obj = get_process(process)

            print(f"Monitoreando {process_obj.name()} (PID {process_obj.pid})")

            if archive.exists():
                archive.unlink()

            # Empezar a leer Metricas y guardarlas
            
            afterburner = subprocess.Popen(
                r'"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe"',
                shell=True
            )
            
            time.sleep(5)

            rtss = get_process("RTSS.exe")
            print(f"RTSS activo PID {rtss.pid}")
            
            while True:
                try:
                    if not process_obj.is_running():
                        print("Juego cerrado")
                        break
                except (psutil.NoSuchProcess, psutil.ZombieProcess):
                    print("Juego cerrado")
                    break

                time.sleep(0.5)

            afterburner.terminate()
            try:
                afterburner.wait(timeout=5)
            except subprocess.TimeoutExpired:
                afterburner.kill()

            afterburner = None

            close_rtss()

            time.sleep(1)

            try:
                createLogCSV(archive, process, pathSafe)
                print("CSV procesado correctamente")
            except Exception as e:
                print(f"Error procesando CSV: {e}")
                
    except KeyboardInterrupt:
        print("El monitoreo ha terminado")

    finally:

        if afterburner is not None:
            print("Cerrando Afterburner...")
            afterburner.terminate()
            try:
                afterburner.wait(timeout=5)
            except subprocess.TimeoutExpired:
                afterburner.kill()

        close_rtss()

def oneshot_monitoring(archive, process, pathSafe, ):

    try:
        # Convertir log de Afterburner a CSV
        createLogCSV(archive, process, pathSafe)

        print("CSV procesado correctamente")

    except Exception as e:
        print(f"Error procesando CSV: {e}")

parser = argparse.ArgumentParser()

parser.add_argument("--archive", required=True)

parser.add_argument("--process", required=True)

parser.add_argument("--pathSafe", required=True)

parser.add_argument(
    "--mode",
    choices=["continuous", "oneshot"],
    default="continuous"
)

args = parser.parse_args()

archive = Path(args.archive)

pathSafe = Path(args.pathSafe)

# preparar entorno

os.makedirs(args.pathSafe, exist_ok=True)

if args.mode == "continuous":
    continuous_monitoring(
        archive,
        args.process,
        pathSafe
    )

elif args.mode == "oneshot":
    oneshot_monitoring(
        archive,
        args.process,
        pathSafe
    )
    
