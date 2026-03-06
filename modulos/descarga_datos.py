import wfdb
import os

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datos')


def descargar_mitdb(registros):
    """Descarga los registros especificados desde PhysioNet"""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    print(f"Verificando registros en: {DATA_PATH}")
    # Descarga los registros (si ya existen, no los vuelve a bajar)
    wfdb.dl_database('mitdb', DATA_PATH, records=registros, overwrite=False)
    print("Descarga completada o registros ya existentes.")


if __name__ == "__main__":
    # Registros pedidos para la Semana 1
    mis_registros = ['100', '105']
    descargar_mitdb(mis_registros)