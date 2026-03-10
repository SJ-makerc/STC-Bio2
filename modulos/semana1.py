import wfdb
import os
import matplotlib.pyplot as plt
import numpy as np

# Configuración de rutas (C:/BIO2/...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datos')
RESULT_PATH = os.path.join(BASE_DIR, 'resultados')


class AdquisicionPhysioNet:
    """
    Clase para la gestión de señales de PhysioNet.
    Aplica conversión manual de 200 ADU/mV y Baseline 1024.
    """

    def __init__(self, nombre_registro):
        self.nombre_reg = nombre_registro
        self.ruta_completa = os.path.join(DATA_PATH, nombre_registro)
        self.record = None
        self.ann = None

    def leer_metadatos(self):
        """Lee el encabezado para obtener información técnica."""
        self.record = wfdb.rdrecord(self.ruta_completa)
        print(f"\n" + "=" * 40)
        print(f"ANÁLISIS DEL REGISTRO: {self.nombre_reg}")
        print(f"Frecuencia de Muestreo: {self.record.fs} Hz")
        print("=" * 40)

    def graficar_señal(self, segundos=10):
        """Genera la gráfica con escala 0.5s / 0.2mV y anotaciones en el tope."""
        muestras = int(self.record.fs * segundos)

        # Lectura de datos crudos (digitales)
        record_data = wfdb.rdrecord(self.ruta_completa, sampto=muestras, physical=False)
        self.ann = wfdb.rdann(self.ruta_completa, 'atr', sampto=muestras)

        # FÓRMULA: (ADU - 1024) / 200
        adu_signal = record_data.d_signal[:, 0].astype(np.float64)
        senal_mv = (adu_signal - 1024) / 200

        tiempo = np.arange(len(senal_mv)) / self.record.fs
        y_min, y_max = min(senal_mv), max(senal_mv)
        rango_y = y_max - y_min

        plt.figure(figsize=(15, 7))

        # Graficar señal principal
        plt.plot(tiempo, senal_mv, color='black', lw=0.9, label=f'Señal ECG ({self.nombre_reg})')

        # Convención de leyenda para las líneas rojas
        plt.plot([], [], color='red', linestyle='--', alpha=0.6, label='Anotaciones MIT (Picos R)')

        # Superponer anotaciones filtrando el símbolo '+'
        for i in range(len(self.ann.sample)):
            simbolo = self.ann.symbol[i]

            # FILTRO: Saltamos la anotación técnica '+' para que no ensucie la gráfica
            if simbolo == '+':
                continue

            pos_x = self.ann.sample[i] / self.record.fs

            # Dibujamos la línea vertical de la anotación
            plt.axvline(x=pos_x, color='red', linestyle='--', alpha=0.3, lw=1)

            # Posicionamos el símbolo (N, A, etc.) en el tope del recuadro (95% de la altura)
            plt.text(pos_x, 0.95, simbolo, color='red', fontweight='bold',
                     ha='center', va='top', transform=plt.gca().get_xaxis_transform())

        # --- CONFIGURACIÓN DE EJES ---
        plt.xlim(0, segundos)
        # Escala horizontal de 0.5 en 0.5 segundos
        plt.xticks(np.arange(0, segundos + 0.5, 0.5))

        # Escala vertical de 0.2 en 0.2 mV
        plt.yticks(np.arange(np.floor(y_min * 5) / 5, np.ceil(y_max * 5) / 5 + 0.4, 0.2))

        # Margen superior para el pasillo de anotaciones
        plt.ylim(y_min - 0.2, y_max + (rango_y * 0.25))

        plt.title(f"ECG Registro {self.nombre_reg}")
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Amplitud (mV)")
        plt.grid(True, which='both', linestyle='--', alpha=0.5)

        plt.legend(loc='upper right', shadow=True)
        plt.tight_layout()

        # Guardado de archivos individuales
        if not os.path.exists(RESULT_PATH):
            os.makedirs(RESULT_PATH)

        nombre_archivo = f'semana1_grafica_{self.nombre_reg}.png'
        ruta_final = os.path.join(RESULT_PATH, nombre_archivo)

        plt.savefig(ruta_final, dpi=300)
        print(f"Archivo guardado exitosamente: {nombre_archivo}")
        plt.show()
        plt.close()


if __name__ == "__main__":
    # Procesamos ambos registros solicitados
    for reg_id in ['100', '105']:
        if os.path.exists(os.path.join(DATA_PATH, f'{reg_id}.hea')):
            obj = AdquisicionPhysioNet(reg_id)
            obj.leer_metadatos()
            obj.graficar_señal(10)
        else:
            print(f"Error: No se encontró el registro {reg_id} en {DATA_PATH}")