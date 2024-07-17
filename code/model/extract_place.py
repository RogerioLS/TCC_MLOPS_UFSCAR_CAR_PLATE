import cv2
from ultralytics import YOLO

model = YOLO('code/model/best.pt')

# Função para extrair a região da placa
def extract_plate(image_path):
    results = model(image_path)
    detections = results[0]

    for detection in detections:
        if detection.names[0] == 'placa':
            x_min, y_min, x_max, y_max = map(int, detection.boxes[0].xyxy[0].tolist())
            img = cv2.imread(image_path)
            plate_img = img[y_min:y_max, x_min:x_max]
            return plate_img

    return None

def main():
    image_path = 'put picture'
    extract_plate(image_path)


if __name__ == "__main__":
    main()