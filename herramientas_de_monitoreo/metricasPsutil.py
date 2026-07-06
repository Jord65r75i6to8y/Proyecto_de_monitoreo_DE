import pandas as pd
import sys
import signal
import os
import psutil
import argparse
import time
import platform

from datetime import datetime

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

def read_Metrics(archive, process, safeInterval):

    if process is None:
        print("Proceso no encontrado")
        exit()

    columnas = [
        "elapsed",
        "OS",
        "CPU",
        "CPU_OS",
        "RAM",
        "RAM_OS",
        "SWAP_OS",
        "I/O_output",
        "I/O_input"
    ]

    if os.path.exists(archive):
        os.remove(archive)

    df = pd.DataFrame(columns=columnas)
    df.to_csv(archive, index=False)

    MB = 1024 * 1024

    disk = process.io_counters()

    prev_read = disk.read_bytes
    prev_write = disk.write_bytes

    # Inicializar mediciones de CPU
    process.cpu_percent(interval=None)
    psutil.cpu_percent(interval=None)

    registros = []
    inicio = time.monotonic_ns()

    while True:
        try:

            ram = process.memory_info()

            mem = psutil.virtual_memory()

            swap = psutil.swap_memory()

            disk = process.io_counters()

            disk_read = disk.read_bytes
            disk_write = disk.write_bytes

            elapsed = (time.monotonic_ns() - inicio) / 1e9

            registros.append([
                round(elapsed, 3),

                os_name,

                process.cpu_percent(interval=None),

                psutil.cpu_percent(interval=None),

                ram.rss / MB,

                mem.used / MB,

                swap.used / MB,

                (disk_write - prev_write) / MB,

                (disk_read - prev_read) / MB
            ])

            prev_read = disk_read
            prev_write = disk_write


            if len(registros) >= safeInterval:

                df_nuevo = pd.DataFrame(
                    registros,
                    columns=columnas
                )

                df = pd.concat(
                    [df, df_nuevo],
                    ignore_index=True
                )

                df.to_csv(archive, index=False)

                registros.clear()

                print(
                    f"[{datetime.now()}] "
                    f"Guardadas {safeInterval} muestras."
                )

            time.sleep(1)

        except (psutil.NoSuchProcess, psutil.ZombieProcess):

            if registros:

                df_nuevo = pd.DataFrame(
                    registros,
                    columns=columnas
                )

                df = pd.concat(
                    [df, df_nuevo],
                    ignore_index=True
                )

                df.to_csv(archive, index=False)

            print("Juego cerrado")

            break

        except Exception as e:
            print(f"Error inesperado: {e}")
            raise

#Leer argumentos

parser = argparse.ArgumentParser()

parser.add_argument("--process", required=True)

parser.add_argument("--pathSafe", required=True)

parser.add_argument("--treatment", required=True)

args = parser.parse_args()

# preparar entorno

os.makedirs(args.pathSafe, exist_ok=True)

while True:

    # Obtener el proceso

    print(f"Esperando el proceso '{args.process}'...")

    process = get_process(args.process)

    print(f"Monitoreando {process.name()} (PID {process.pid})")

    # Generar nombre del archivo 

    os_name = platform.system()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    archive = os.path.join(
        args.pathSafe,
        f"{process.name()}_monitor_{os_name}_{args.treatment}_{timestamp}.csv"
    )

    # Empezar a leer Metricas y guardarlas

    read_Metrics(archive, process, 300)

    print(f"Se ha guardado el archivo: {archive} en la carpeta correspondiente")