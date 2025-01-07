import cv2 
from picamera2 import Picamera2

def stream_video():
    picam = Picamera2()
    picam.preview_configuration.main.size = (1280, 720)
    picam.preview_configuration.main.format = "RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()

    photo_counter = 0  # Contador para las fotos

    while True:
        frame = picam.capture_array()
        cv2.imshow("picam", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):  # Salir al presionar 'q'
            break
        elif key == ord('s'):  # Guardar foto al presionar 's'
            photo_counter += 1
            filename = f"captured_image_{photo_counter}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Foto guardada como {filename}")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    stream_video()