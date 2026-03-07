# STC-Sierra: Sistema de Tele-Triaje Cardíaco

Este proyecto busca mejorar la atención cardiológica en las zonas de difícil acceso del departamento del **Cesar**, Colombia.

## Problema Clínico
En la Sierra Nevada y la Serranía del Perijá, el acceso a especialistas es limitado. Este módulo permite procesar señales ECG digitales para facilitar un pre-diagnóstico remoto (Tele-Triaje).

## Instrucciones de Ejecución
1. Configurar el entorno: `conda create -n stcsierra python=3.10`
2. Instalar dependencias: `pip install -r requirements.txt`
3. Descargar datos: Ejecutar `python modulos/descarga_datos.py`
4. Procesar Semana 1: Ejecutar `python modulos/semana1.py`