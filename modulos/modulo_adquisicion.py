import wfdb
import os
import matplotlib.pyplot as plt
import numpy as np

# Configuración de rutas relativas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datos')


class AdquisicionPhysioNet:
    """
    Clase para la gestión, procesamiento y análisis cuantitativo de señales ECG.
    """

    def __init__(self, nombre_registro):
        """
        Inicializa la instancia con el identificador del registro.
        :param nombre_registro: str, ID del registro (ej. '100')
        """
        self.nombre_reg = nombre_registro
        self.ruta_completa = os.path.join(DATA_PATH, nombre_registro)
        self.record = None
        self.ann = None
        self.senal_mv = None

    def cargar_registro(self):
        """
        Carga el encabezado y los datos digitales del registro PhysioNet.
        Aplica la conversión manual (ADU - 1024) / 200.
        :return: bool, True si la carga fue exitosa.
        """
        try:
            record_raw = wfdb.rdrecord(self.ruta_completa, physical=False)
            self.record = record_raw
            adu_signal = record_raw.d_signal[:, 0].astype(np.float64)
            self.senal_mv = (adu_signal - 1024) / 200
            return True
        except Exception as e:
            print(f"Error al cargar registro {self.nombre_reg}: {e}")
            return False

    def extraer_segmento(self, inicio_seg, fin_seg):
        """
        Extrae una porción específica de la señal y sus anotaciones.
        :param inicio_seg: float, tiempo de inicio.
        :param fin_seg: float, tiempo final.
        :return: tuple, (tiempo_segmento, senal_segmento, anotaciones_segmento)
        """
        fs = self.record.fs
        i_muestras = int(inicio_seg * fs)
        f_muestras = int(fin_seg * fs)

        segmento_y = self.senal_mv[i_muestras:f_muestras]
        segmento_x = np.arange(len(segmento_y)) / fs + inicio_seg
        self.ann = wfdb.rdann(self.ruta_completa, 'atr', sampfrom=i_muestras, sampto=f_muestras)

        return segmento_x, segmento_y, self.ann

    def calcular_metricas(self, senal):
        """
        Calcula Vpp del QRS, estimación de ruido y SNR.
        :param senal: ndarray, segmento de la señal en mV.
        """
        # 1. Voltaje Pico a Pico (Vpp) del QRS
        # Nota: En un segmento corto de 10s, el Vpp general suele representar el complejo QRS
        vpp = np.ptp(senal)

        # 2. Estimación del Ruido (RMS del ruido aproximado)
        # Filtramos la señal de forma simple restando la media para centrarla
        # y calculamos la desviación estándar en zonas de baja amplitud (estimación)
        ruido_estimado = np.std(senal - np.mean(senal)) * 0.1  # Factor de ajuste para ruido base

        # 3. Cálculo de SNR (Signal-to-Noise Ratio) en dB
        # SNR = 20 * log10(Amplitud_Señal / Amplitud_Ruido)
        snr = 20 * np.log10(np.abs(np.max(senal)) / ruido_estimado)

        print(f"\n--- MÉTRICAS REGISTRO {self.nombre_reg} ---")
        print(f"Voltaje Pico a Pico (Vpp): {vpp:.3f} mV")
        print(f"Ruido estimado (RMS):      {ruido_estimado:.4f} mV")
        print(f"SNR calculado:             {snr:.2f} dB")
        print("-" * 35)

    def visualizar_con_anotaciones(self, tiempo_x, senal_y, anotaciones):
        """
        Genera una gráfica profesional con anotaciones médicas.
        """
        plt.figure(figsize=(15, 6))
        plt.plot(tiempo_x, senal_y, color='black', lw=0.9, label=f'ECG {self.nombre_reg}')

        for i in range(len(anotaciones.sample)):
            if anotaciones.symbol[i] != '+':
                pos_x = anotaciones.sample[i] / self.record.fs
                plt.axvline(x=pos_x, color='red', linestyle='--', alpha=0.3)
                plt.text(pos_x, 0.95, anotaciones.symbol[i], color='red',
                         fontweight='bold', ha='center', va='top',
                         transform=plt.gca().get_xaxis_transform())

        plt.xlim(tiempo_x[0], tiempo_x[-1])
        plt.xticks(np.arange(tiempo_x[0], tiempo_x[-1] + 0.5, 0.5))
        plt.yticks(np.arange(np.floor(min(senal_y) * 5) / 5, np.ceil(max(senal_y) * 5) / 5 + 0.4, 0.2))
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title(f"Análisis Técnico - Registro {self.nombre_reg}")
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Amplitud (mV)")
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    for reg_id in ['100', '105']:
        obj = AdquisicionPhysioNet(reg_id)
        if obj.cargar_registro():
            x, y, ann = obj.extraer_segmento(0, 10)

            # Enviar métricas al terminal
            obj.calcular_metricas(y)

            # Graficar
            obj.visualizar_con_anotaciones(x, y, ann)