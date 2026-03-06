import wfdb
import os
import matplotlib.pyplot as plt
import numpy as np

# 1. CONFIGURACIÓN DE RUTAS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datos')
RESULT_PATH = os.path.join(BASE_DIR, 'resultados')

if not os.path.exists(RESULT_PATH):
    os.makedirs(RESULT_PATH)


def graficar_semana_1(nombre_reg, segundos=10):
    ruta_reg = os.path.join(DATA_PATH, nombre_reg)

    # --- PUNTO 2: LECTURA Y EXTRACCIÓN DE METADATOS ---
    # Leemos el registro completo para extraer la info del encabezado (.hea)
    record = wfdb.rdrecord(ruta_reg)

    # Extracción de variables requeridas
    fs = record.fs
    unidades = record.units[0]  # Usualmente 'mV'
    n_derivaciones = record.n_sig
    nombres_deriv = record.sig_name
    duracion_seg = record.sig_len / fs

    # Impresión en consola según requerimiento de la guía
    print(f"\n" + "=" * 40)
    print(f"ANÁLISIS DEL REGISTRO: {nombre_reg}")
    print(f"Frecuencia de Muestreo: {fs} Hz")
    print(f"Duración Total: {duracion_seg:.2f} segundos")
    print(f"Número de Derivaciones: {n_derivaciones}")
    print(f"Nombres de Derivaciones: {nombres_deriv}")
    print(f"Unidades de la Señal: {unidades}")
    print("=" * 40)

    # --- PUNTO 3: VISUALIZACIÓN ---
    # Volvemos a leer solo los 10 segundos para la gráfica
    muestras_10s = int(fs * segundos)
    record_plot = wfdb.rdrecord(ruta_reg, sampto=muestras_10s)
    ann = wfdb.rdann(ruta_reg, 'atr', sampto=muestras_10s)

    tiempo = np.arange(len(record_plot.p_signal)) / fs
    senal = record_plot.p_signal[:, 0]

    plt.figure(figsize=(12, 5))
    plt.plot(tiempo, senal, color='black', lw=0.8)

    # Superponer anotaciones (Líneas rojas y símbolos)
    for i in range(len(ann.sample)):
        posicion_x = ann.sample[i] / fs
        plt.axvline(x=posicion_x, color='red', linestyle='--', alpha=0.5)
        plt.text(posicion_x, max(senal), ann.symbol[i],
                 color='red', fontweight='bold', horizontalalignment='center')

    plt.title(f"Visualización Semana 1 - Registro {nombre_reg} ({segundos} segundos)")
    plt.xlabel("Tiempo (s)")
    plt.ylabel(f"Amplitud ({unidades})")  # Usamos las unidades extraídas del .hea
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(os.path.join(RESULT_PATH, f'grafica_semana1_{nombre_reg}.png'))
    plt.show()


if __name__ == "__main__":
    if os.path.exists(os.path.join(DATA_PATH, '100.hea')):
        graficar_semana_1('100')
        graficar_semana_1('105')
    else:
        print("Error: Registros no encontrados. Ejecuta primero descarga_datos.py")