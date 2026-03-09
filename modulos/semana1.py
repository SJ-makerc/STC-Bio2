import wfdb
import os
import matplotlib.pyplot as plt
import numpy as np

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datos')
RESULT_PATH = os.path.join(BASE_DIR, 'resultados')


class AdquisicionPhysioNet:
    """
    Clase para gestionar la descarga, lectura y visualización de señales
    provenientes de la base de datos MIT-BIH de PhysioNet.
    """

    def __init__(self, nombre_registro):
        """
        Inicializa la clase con el nombre del registro y define las rutas.
        :param nombre_registro: ID del registro (ej. '100')
        """
        self.nombre_reg = nombre_registro
        self.ruta_completa = os.path.join(DATA_PATH, nombre_registro)
        self.record = None
        self.ann = None

    def leer_metadatos(self):
        """
        Lee el archivo .hea y extrae la frecuencia de muestreo y metadatos.
        Imprime la información técnica en la consola.
        """
        self.record = wfdb.rdrecord(self.ruta_completa)
        fs = self.record.fs
        unidades = self.record.units[0]
        n_derivaciones = self.record.n_sig
        duracion_seg = self.record.sig_len / fs

        print(f"\n" + "=" * 40)
        print(f"ANÁLISIS DEL REGISTRO: {self.nombre_reg}")
        print(f"Frecuencia de Muestreo: {fs} Hz")
        print(f"Duración Total: {duracion_seg:.2f} segundos")
        print(f"Número de Derivaciones: {n_derivaciones}")
        print(f"Unidades de la Señal: {unidades}")
        print("=" * 40)

    def graficar_señal(self, segundos=10):
        """
        Genera una gráfica de la señal en mV con sus respectivas anotaciones.
        Ajusta los ejes para eliminar espacios desaprovechados.
        :param segundos: Cantidad de tiempo a visualizar.
        """
        muestras = int(self.record.fs * segundos)
        record_plot = wfdb.rdrecord(self.ruta_completa, sampto=muestras)
        self.ann = wfdb.rdann(self.ruta_completa, 'atr', sampto=muestras)

        tiempo = np.arange(len(record_plot.p_signal)) / self.record.fs
        senal = record_plot.p_signal[:, 0]

        plt.figure(figsize=(12, 5))

        # Graficar la señal
        plt.plot(tiempo, senal, color='black', lw=0.9, label=f'ECG (Canal {record_plot.sig_name[0]})')

        # Superponer anotaciones
        for i in range(len(self.ann.sample)):
            pos_x = self.ann.sample[i] / self.record.fs
            plt.axvline(x=pos_x, color='red', linestyle='--', alpha=0.4, lw=1)

            # Solo etiquetar la primera anotación en la leyenda
            label_text = 'Anotación MIT' if i == 0 else ""
            if i == 0:
                plt.plot([], [], color='red', linestyle='--', alpha=0.4, label='Anotaciones MIT')

            plt.text(pos_x, max(senal), self.ann.symbol[i], color='red',
                     fontweight='bold', horizontalalignment='center')

        # --- MEJORA DE EJES Y LÍMITES ---
        plt.xlim(0, segundos)  # AJUSTE CLAVE: Elimina los espacios a los lados

        plt.title(f"Visualización Semana 1 - Registro {self.nombre_reg}")
        plt.xlabel("Tiempo (s)")
        plt.ylabel(f"Amplitud ({self.record.units[0]})")
        plt.grid(True, which='both', linestyle=':', alpha=0.5)
        plt.legend(loc='upper right')

        plt.tight_layout()

        if not os.path.exists(RESULT_PATH):
            os.makedirs(RESULT_PATH)

        nombre_archivo = f'grafica_{self.nombre_reg}.png'
        plt.savefig(os.path.join(RESULT_PATH, nombre_archivo), bbox_inches='tight')
        plt.show()


if __name__ == "__main__":
    for reg_id in ['100', '105']:
        if os.path.exists(os.path.join(DATA_PATH, f'{reg_id}.hea')):
            obj = AdquisicionPhysioNet(reg_id)
            obj.leer_metadatos()
            obj.graficar_señal(10)
        else:
            print(f"Error: No se encuentra el registro {reg_id}")