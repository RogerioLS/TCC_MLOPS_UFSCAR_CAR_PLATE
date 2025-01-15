import os
import json
import boto3
import io
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from ultralytics import YOLO
from typing import Optional

class PlateDetection:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('plate-detection-info-prod')
        self.model_path = '/var/task/yolov8_model.pt'
        self.model = YOLO(self.model_path)
        self.yolo_config_dir = "/tmp"
        os.environ['YOLO_CONFIG_DIR'] = self.yolo_config_dir

    def save_metadata(self, bucket_name: str, image_key: str, unique_id: str) -> None:
        """
        Save metadata to S3.

        Args:
            bucket_name (str): The name of the S3 bucket.
            image_key (str): The key of the image in the S3 bucket.
            unique_id (str): The unique identifier for the metadata.

        Returns:
            None
        """
        metadata = {
            "timestamp": unique_id,
            "image_name": os.path.basename(image_key)
        }

        metadata_json = json.dumps(metadata)
        metadata_key = f"metadata/{os.path.basename(image_key)}.metadata.json"

        self.s3_client.put_object(
            Bucket=bucket_name,
            Key=metadata_key,
            Body=metadata_json,
            ContentType='application/json'
        )

        print(f"Metadata saved to S3: {metadata_key}")

    def save_image_data(self, image_key: str, image_path: str, plate_key: str, detected: int) -> str:
        """
        Save image data to DynamoDB.

        Args:
            image_key (str): The key of the image in the S3 bucket.
            image_path (str): The URL of the image in the S3 bucket.
            plate_key (str): The key of the cropped plate image in the S3 bucket.
            detected (int): Whether a plate was detected (1) or not (0).

        Returns:
            str: The timestamp when the data was saved.
        """
        timestamp = datetime.utcnow().isoformat()

        self.table.put_item(
            Item={
                'PK': image_key,
                'timestamp': timestamp,
                'image_path': image_path,
                'cropped_image_path': plate_key,
                'detected': detected
            }
        )
        return timestamp

    def process_image(self, bucket_name: str, image_key: str) -> None:
        """
        Process the image to detect plates and save results.

        Args:
            bucket_name (str): The name of the S3 bucket.
            image_key (str): The key of the image in the S3 bucket.

        Returns:
            None
        """
        response = self.s3_client.get_object(Bucket=bucket_name, Key=image_key)
        img_data = response['Body'].read()

        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        results = self.model(img)
        detections = results[0]
        plate_detected = 0

        for detection in detections:
            if detection.names[0] == 'placa':
                print("Plate detected!!!")
                plate_detected = 1
                x_min, y_min, x_max, y_max = map(int, detection.boxes[0].xyxy[0].tolist())
                plate_img = img[y_min:y_max, x_min:x_max]

                pil_image = Image.fromarray(plate_img)
                buf = io.BytesIO()
                pil_image.save(buf, format='JPEG')
                buf.seek(0)

                plate_key = os.path.basename(image_key)
                bucket_plate_name = "upload-image-second-stage-prod"

                self.s3_client.upload_fileobj(buf, bucket_plate_name, plate_key, ExtraArgs={'ContentType': 'image/jpeg'})

                file_url = f"https://{bucket_plate_name}.s3.amazonaws.com/{plate_key}"
                timestamp = self.save_image_data(image_key, f"https://{bucket_name}.s3.amazonaws.com/{image_key}", file_url, plate_detected)
                self.save_metadata(bucket_plate_name, plate_key, timestamp)

        if plate_detected == 0:
            print("Plate NOT detected!!!")
            self.save_image_data(image_key, f"https://{bucket_name}.s3.amazonaws.com/{image_key}", "", plate_detected)

def lambda_handler(event: dict, context: Optional[object]) -> None:
    """
    AWS Lambda handler function.

    Args:
        event (dict): The event data.
        context (Optional[object]): The context object.

    Returns:
        None 
    """
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_key = event['Records'][0]['s3']['object']['key']
    print("detectPlate ", bucket_name)
    print("detectPlate ", image_key)

    plate_detection = PlateDetection()
    plate_detection.process_image(bucket_name, image_key)
