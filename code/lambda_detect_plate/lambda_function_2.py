import boto3
import torch
import os
from PIL import Image
import numpy as np
from torchvision import transforms

s3 = boto3.client('s3')

YOLOV8_DIR = '/tmp'

# Set or modify the value of YOLO_CONFIG_DIR
os.environ['YOLO_CONFIG_DIR'] = "/tmp"
# Verify that the value has been updated
print(f"YOLO_CONFIG_DIR: {os.getenv('YOLO_CONFIG_DIR')}")

# Carregar o modelo YOLOv8
model_path = '/var/task/yolov8_model.pt'
model = torch.load(model_path)

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_key = event['Records'][0]['s3']['object']['key']
    
    print ("lambda_handler ", image_key)
    # Baixar a imagem do bucket
    download_path = f'/tmp/{image_key}'
    s3.download_file(bucket_name, image_key, download_path)
    print ("lambda_handler 2")
    
    # Carregar a imagem
    image = Image.open(download_path)
    print ("lambda_handler 3")
    transform = transforms.Compose([
        transforms.Resize((640, 640)),
        transforms.ToTensor()
    ])
    print ("lambda_handler 4")
    img_tensor = transform(image).unsqueeze(0)
    print ("lambda_handler 5")
    
    # Realizar a inferência
    with torch.no_grad():
        pred = model(img_tensor)
    print ("lambda_handler 6")
    # Verificar se há placas
    if is_plate_detected(pred):
        print ("lambda_handler 7")
        # Salvar a imagem ou resultados no segundo bucket
        result_key = f"results/{image_key}"
        s3.upload_file(download_path, 'output-bucket-name', result_key)
    print ("lambda_handler 8")
def is_plate_detected(pred):
    # Implementar a lógica para verificar se há uma placa
    pass
