import os
import json
import boto3
import io
import cv2
import numpy as np
from PIL import Image
import uuid
from datetime import datetime

s3_client = boto3.client('s3')

YOLOV8_DIR = '/tmp'

# Set or modify the value of YOLO_CONFIG_DIR
os.environ['YOLO_CONFIG_DIR'] = "/tmp"
# Verify that the value has been updated
print(f"YOLO_CONFIG_DIR: {os.getenv('YOLO_CONFIG_DIR')}")

from ultralytics import YOLO

# Define model path YOLOv8
MODEL_PATH = '/var/task/yolov8_model.pt'
modelPlate = YOLO('/var/task/yolov8_model.pt')
print(f"MODEL_PATH: {MODEL_PATH}")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('plate-detection-info-prod')

def save_metadata(bucket_name, image_key, unique_id):
    metadata = {
        "timestamp": unique_id,
        "image_name": os.path.basename(image_key)
    }

    # Converter o dicionário para JSON
    metadata_json = json.dumps(metadata)

    # Salvar o arquivo JSON no S3
    metadata_key = f"metadata/{os.path.basename(image_key)}.metadata.json"

    # Upload do JSON para o S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=metadata_key,
        Body=metadata_json,
        ContentType='application/json'
    )

    print(f"Metadata saved to S3: {metadata_key}")


def save_image_data(image_key, image_path, plate_key, detected):
    # Timestamp atual
    timestamp = datetime.utcnow().isoformat()

    # Salvar os dados no DynamoDB
    table.put_item(
        Item={
            'PK': image_key,
            'timestamp': timestamp,
            'image_path': image_path,
            'cropped_image_path': plate_key,
            'detected': detected
        }
    )
    return timestamp


def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_key = event['Records'][0]['s3']['object']['key']
    print ("detectPlate ", bucket_name)
    print ("detectPlate ", image_key)
   
    response = s3_client.get_object(Bucket=bucket_name, Key=image_key)
    img_data = response['Body'].read()
        
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    results = modelPlate(img)
    detections = results[0]
    plate_detected = 0

    for detection in detections:
        print ("detection.name =", detection.names[0] )
        if detection.names[0] == 'placa':
            print ("Plate detected!!!")
            plate_detected = 1
            x_min, y_min, x_max, y_max = map(int, detection.boxes[0].xyxy[0].tolist())
            plate_img = img[y_min:y_max, x_min:x_max]
            
            pil_image = Image.fromarray(plate_img)
            buf = io.BytesIO()
            pil_image.save(buf, format='JPEG')
            buf.seek(0)
        
            # Define the new S3 object key for the plate images
            plate_key = os.path.basename(image_key)

            bucket_plate_name = "upload-image-second-stage-dev"

            # Upload the annotated image back to S3
            s3_client.upload_fileobj(buf, bucket_plate_name, plate_key, ExtraArgs={'ContentType': 'image/jpeg'})
        
            # Return the URL of the uploaded annotated image
            file_url = f"https://{bucket_plate_name}.s3.amazonaws.com/{plate_key}"

            timestamp= save_image_data(image_key,f"https://{bucket_name}.s3.amazonaws.com/{image_key}", file_url, plate_detected)

            save_metadata(bucket_plate_name, plate_key, timestamp)

    if (plate_detected == 0):
        print ("Plate NOT detected!!!")
        save_image_data(image_key, f"https://{bucket_name}.s3.amazonaws.com/{image_key}","", plate_detected)
