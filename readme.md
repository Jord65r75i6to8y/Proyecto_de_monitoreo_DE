# Proyecto de Monitoreo y Análisis del Impacto de la Reducción de Memoria RAM en Don't Starve Together Offline

**Autor:** Jordan Barquero Araya  
**Carné:** C30965

## Descripción

Este proyecto tiene como objetivo analizar el impacto que la reducción de memoria RAM y el sistema operativo tienen sobre el desempeño del videojuego **Don't Starve Together Offline**.

Para ello, se realizaron múltiples tratamientos tanto en **Ubuntu 24.04** como en **Windows 11**, limitando la memoria disponible para Steam y sus procesos asociados, mientras se monitoreaban diferentes métricas de rendimiento y uso de recursos del sistema.

Las principales variables analizadas fueron:

- FPS
- Frametime
- Uso de memoria RAM
- Uso de memoria virtual (Swap/Pagefile)
- Uso de CPU
- Lectura y escritura de disco


# Monitores utilizados

## Linux (Ubuntu 24.04)

* MangoHud (FPS y Frametime)

* Psutil (RAM, Swap, CPU y Disco)

## Windows 11

* MSI Afterburner + RivaTuner Statistics Server (FPS y Frametime)

* Psutil (RAM, Swap, CPU y Disco)

# Proyecto de Monitoreo

El análisis completo de los datos puede consultarse en Google Colab:

[PROYECTO-DESEMPEÑO_Y_EXPERIMENTACION.ipynb](https://colab.research.google.com/drive/17mnEaE6GPpwcLBCdIKfQnL1YOzIx4-SY?usp=sharing)