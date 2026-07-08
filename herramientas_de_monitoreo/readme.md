# comandos a ejecutar

- python3 metricasPsutil.py 
    --process PROCESO_A_MONITOREAR 
    --pathSafe RUTA_DONDE_GUARDAR 
    --treatment NOMBRE_IDENTIFICADOR_TRATAMIENTO

- python3 mergeMetricas.py 
    --pathGet RUTA_DONDE EXTRAER 
    --pathSafe RUTA_DONDE_GUARDAR

- Recordar configurar MangoHub en opciones de lanzamiento de Steam: 
    mangohud %command%

python MSIafterBurnerToCSV.py `
    --archive ARCHIVO_DONDE_EXTRAER_DATOS
    --process PROCESO_A_MONITOREAR 
    --pathSafe RUTA_DONDE_GUARDAR_CSV

- Recordar tener instalado afterburner y RTSS 

## archivos auxiliares

corregir.py
  --path RUTA_ARCHIVOS_A_CORREGIR

Use este script para corregir fallos que se presentaron en los archivos provenientes de windows
    --elapse en lugar de elapsed
    --nombre del archivo, fecha en formato erroneo*

WinJobMemory.ps1

Delimita la cantidad de memoria ram a la que tiene acceso un proceso o este caso steam

powershell -ExecutionPolicy Bypass -File .\WinJobMemory.ps1 -MemoryLimitMB 3600 