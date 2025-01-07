import cv2
import numpy as np
import skimage.feature
import skimage.color
import time
from picamera2 import Picamera2

# Función para detectar si el color está presente en la imagen
def is_color_detected(mask):
    return cv2.countNonZero(mask) > 5  # Verifica si hay píxeles no nulos

# Función para dilatar la imagen
def custom_dilate(img: np.array, kernel_size: int = 60) -> np.array:
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    dilated = cv2.dilate(img, kernel, iterations=1)
    return dilated

# Función para detectar si es un cuadrado (cara de un cubo de Rubik)
def is_square_detected(canny_edges):
    contours, _ = cv2.findContours(canny_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > 1000:
                (x, y, w, h) = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                if 0.9 <= aspect_ratio <= 1.1:
                    return True
    return False

def security_system(picam):    
    # Definir rango de colores
    light_blue = (100, 150, 50)  
    dark_blue = (130, 255, 255)  
    light_yellow = (26, 100, 100)
    dark_yellow = (35, 255, 255)
    light_green = (35, 100, 50)
    dark_green = (85, 255, 255)

    # Estados del sistema de seguridad
    security_state = 0  # 0 = espera azul, 1 = espera amarillo, 2 = espera verde

    # Variables para calcular FPS
    fps = 0
    prev_time = time.time()

    # Procesar cada fotograma del video
    while True:
        # Capturar el fotograma del video
        frame = picam.capture_array()

        # Calcular FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # Convertir la imagen a espacio de color HSV
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        # Crear máscaras para los colores
        blue_mask = cv2.inRange(hsv_img, light_blue, dark_blue)
        yellow_mask = cv2.inRange(hsv_img, light_yellow, dark_yellow)
        green_mask = cv2.inRange(hsv_img, light_green, dark_green)
        
        # Combinar las máscaras de colores
        color_mask = cv2.bitwise_or(cv2.bitwise_or(blue_mask, yellow_mask), green_mask)
        
        # Convertir a escala de grises
        gray_img = skimage.color.rgb2gray(frame)
        gray_img = (gray_img * 255).astype(np.uint8)  # Convertir a uint8
        
        # Aplicar el filtro Canny
        canny_edges = skimage.feature.canny(gray_img / 255.0)
        canny_edges_display = (canny_edges * 255).astype(np.uint8)
        
        # Aplico dilatación a los bordes detectados
        canny_edges_dilated = custom_dilate(canny_edges_display)
        
        # Detectar si se ha encontrado el patrón de una cara de Rubik
        rubiks_detected = is_square_detected(canny_edges_dilated)

        if rubiks_detected:
            print(f"Rubik's Face Detected: {rubiks_detected}")
            blue_detected = is_color_detected(blue_mask)
            yellow_detected = is_color_detected(yellow_mask)
            green_detected = is_color_detected(green_mask)

            if security_state == 0 and blue_detected:
                print("Paso 1: Color azul detectado.")
                security_state = 1
                time.sleep(5)
            elif security_state == 1 and green_detected:
                print("Paso 2: Color amarillo detectado.")
                security_state = 2
                time.sleep(5)
            elif security_state == 2 and green_detected:
                print("Paso 3: Color verde detectado. Sistema desbloqueado.")
                frame = picam.capture_array()
                cv2.imshow("Original Image", frame)
                time.sleep(15)
                break
            elif blue_detected or yellow_detected or green_detected:
                print("Secuencia incorrecta. Reiniciando sistema.")
                time.sleep(5)
                security_state = 0  # Reiniciar si los colores están fuera de orden
            else:
                
                security_state = 0

        # Mostrar las imágenes en tiempo real con FPS
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Original Image", frame)
        cv2.imshow("Canny Edge Detection", canny_edges_display)
        cv2.imshow("Canny Edge Dilated", canny_edges_dilated)

        # Si presionas 'q', se detendrá el video
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def tracker(picam):
    # Cargar el detector de personas HOG + SVM desde OpenCV
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # Inicializar el rastreador 
    tracker = cv2.TrackerCSRT_create()

    # Inicializar el estado de detección
    detector_initialized = False

    # Variables para calcular FPS
    fps_display = 0
    prev_time = time.time()

    while True:
        frame = picam.capture_array()
        frame_resized = cv2.resize(frame, (640, 360))

        # Calcular FPS
        current_time = time.time()
        time_difference = current_time - prev_time
        if time_difference > 0:
            fps_display = 1 / time_difference
        prev_time = current_time

        # Detectar peatones en el fotograma actual
        boxes, weights = hog.detectMultiScale(frame_resized, winStride=(8, 8), padding=(4, 4), scale=1.05)

        if len(boxes) > 0 and not detector_initialized:
            # Seleccionar el primer peatón detectado
            bbox = boxes[0]
            x, y, w, h = bbox
            tracker.init(frame_resized, bbox)
            detector_initialized = True
            print(f"Peatón detectado en: {bbox}")

        # Si el tracker está inicializado, actualizar el rastreador
        if detector_initialized:
            success, bbox = tracker.update(frame_resized)

            if success:
                x, y, w, h = map(int, bbox)
                cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame_resized, "Tracking", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame_resized, "Lost", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Mostrar FPS en el fotograma
        cv2.putText(frame_resized, f"FPS: {fps_display:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Mostrar el resultado
        cv2.imshow("Tracking", frame_resized)

        # Salir si se presiona 'q'
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    # Configuración de la cámara
    picam = Picamera2()
    picam.preview_configuration.main.size = (1280, 720)
    picam.preview_configuration.main.format = "RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()

    # Llamada al sistema de seguridad
    security_system(picam)
    print("Accediendo al sistema de Seguimiento de Peatones")
    time.sleep(15)

    # Llamada al tracker
    tracker(picam)

    # Fin del Programa
    picam.stop()
    cv2.destroyAllWindows()
