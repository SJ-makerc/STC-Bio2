import wfdb
import os
import matplotlib.pyplot as plt
import numpy as np

# Rutas relativas para evitar rutas absolutas del PC
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datos')
RESULT_PATH = os.path.join(BASE_DIR, 'resultados')


class AdquisicionPhysioNet:
    """
    Clase para la gestión y procesamiento de señales de la base de datos MIT-BIH.
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
        :return: bool, True si la carga fue exitosa, False en caso contrario.
        """
        try:
            # physical=False para obtener datos crudos (ADU)
            record_raw = wfdb.rdrecord(self.ruta_completa, physical=False)
            self.record = record_raw

            # Conversión a mV (Fórmula Semana 1)
            adu_signal = record_raw.d_signal[:, 0].astype(np.float64)
            self.senal_mv = (adu_signal - 1024) / 200

            print(f"Registro {self.nombre_reg} cargado exitosamente.")
            return True
        except Exception as e:
            print(f"Error al cargar registro: {e}")
            return False

    def extraer_segmento(self, inicio_seg, fin_seg):
        """
        Extrae una porción específica de la señal y sus anotaciones.
        :param inicio_seg: float, tiempo de inicio en segundos.
        :param fin_seg: float, tiempo final en segundos.
        :return: tuple, (tiempo_segmento, senal_segmento, anotaciones_segmento)
        """
        fs = self.record.fs
        i_muestras = int(inicio_seg * fs)
        f_muestras = int(fin_seg * fs)

        # Extraer segmento de señal y anotaciones
        segmento_y = self.senal_mv[i_muestras:f_muestras]
        segmento_x = np.arange(len(segmento_y)) / fs + inicio_seg
        self.ann = wfdb.rdann(self.ruta_completa, 'atr', sampfrom=i_muestras, sampto=f_muestras)

        return segmento_x, segmento_y, self.ann

    def visualizar_con_anotaciones(self, tiempo_x, senal_y, anotaciones):
        """
        Genera una gráfica profesional del segmento procesado.
        :param tiempo_x: ndarray, vector de tiempo.
        :param senal_y: ndarray, vector de amplitud en mV.
        :param anotaciones: object, objeto de anotaciones de wfdb.
        """
        plt.figure(figsize=(15, 6))
        plt.plot(tiempo_x, senal_y, color='black', lw=0.9, label='ECG')

        y_max = max(senal_y)
        for i in range(len(anotaciones.sample)):
            if anotaciones.symbol[i] != '+':
                pos_x = anotaciones.sample[i] / self.record.fs
                plt.axvline(x=pos_x, color='red', linestyle='--', alpha=0.3)
                plt.text(pos_x, 0.95, anotaciones.symbol[i], color='red',
                         fontweight='bold', ha='center', va='top',
                         transform=plt.gca().get_xaxis_transform())

        plt.xlim(tiempo_x[0], tiempo_x[-1])
        plt.xticks(np.arange(tiempo_x[0], tiempo_x[-1] + 0.5, 0.5))
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title(f"Módulo Adquisición - Análisis Registro {self.nombre_reg}")
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Amplitud (mV)")
        plt.show()


if __name__ == "__main__":
    # Definimos los registros que queremos procesar
    registros_objetivo = ['100', '105']

    for reg_id in registros_objetivo:
        # 1. Creamos el objeto para el registro actual
        obj = AdquisicionPhysioNet(reg_id)

        # 2. Intentamos cargar los datos
        if obj.cargar_registro():
            # 3. Extraemos un segmento de 10 segundos (del 0 al 10)
            # Aquí es donde usamos el nuevo metodo extraer_segmento
            x, y, ann = obj.extraer_segmento(4, 6)

            # 4. Visualizamos con el formato profesional
            obj.visualizar_con_anotaciones(x, y, ann)

            print(f"Procesamiento de registro {reg_id} completado.\n")