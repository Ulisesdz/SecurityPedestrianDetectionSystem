# Proyecto Final de Visión por Computador

Este repositorio contiene el proyecto final de la asignatura de Visión por Computador, realizado por **Ignacio Felices Vera** y **Ulises Díez Santaolalla**. El proyecto incluye dos sistemas principales desarrollados en Python utilizando OpenCV y otras librerías de procesamiento de imágenes:

1. **Sistema de Seguridad Basado en Detección de Colores y Figuras**
2. **Seguimiento de Peatones usando HOG + SVM y Rastreador CSRT**

---

## Estructura del Repositorio

- `src/`
  - `Obtain_Photos.py`: Obtenicón de fotos para la calibración.
  - `test.py`: Prueba de la cámara de la Raspberry Pi.
  - `Vision_FProject.py`: Código principal que integra el sistema de seguridad y el seguimiento de peatones.
  - `Proyecto_estructura.ipynb`: Notebook con el desarrollo por partes del proyecto.
    
- `data/`
  - Carpetes con imágenes para la calibración de la cámara, con la deteccion de los colores del cubo Rubik, y el resultado de los trackers
- `docs/`
  - `informe.pdf`: Informe detallado sobre el desarrollo y resultados del proyecto.
- `videos/`
  -   Videos para la prueba y funcionamiento del tracker

---

## Descripción de los Sistemas

### 1. Sistema de Seguridad Basado en Detección de Colores y Figuras

Este sistema detecta patrones de color específicos (azul, amarillo y verde) y reconoce figuras cuadradas (caras de un cubo de Rubik). Implementa una secuencia de seguridad donde:

- **Paso 1**: Detecta el color azul.
- **Paso 2**: Detecta el color amarillo.
- **Paso 3**: Detecta el color verde para desbloquear el sistema.

#### Tecnologías usadas:
- OpenCV para procesamiento de imágenes.
- Detección de bordes con el algoritmo de Canny.
- Detección de contornos y reconocimiento de formas geométricas.

---

### 2. Seguimiento de Peatones

El sistema utiliza un detector HOG + SVM para localizar peatones en tiempo real y los sigue mediante el rastreador CSRT.

#### Tecnologías usadas:
- Detector de peatones basado en HOG (Histogram of Oriented Gradients).
- Rastreador CSRT para seguimiento en tiempo real.

---

## Requisitos

Instalar las siguientes dependencias:

```bash
pip install opencv-python-headless numpy scikit-image picamera2
