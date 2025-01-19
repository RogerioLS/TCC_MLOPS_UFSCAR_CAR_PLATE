"""Módulo para a função Lambda de reconhecimento de placas de carro usando PaddleOCR."""

import json
import os
import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

import boto3
import cv2
import numpy as np
from paddleocr import PaddleOCR


class OCRPlateDetection:
    """Classe para reconhecimento de placas de carro usando PaddleOCR."""

    def __init__(self):
        """Inicializa a instância do OCRPlateDetection."""
        self.s3_client = boto3.client("s3")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table("plate-detection-info-prod")
        self.model_dir = "/tmp/.paddleocr"
        os.makedirs(self.model_dir, exist_ok=True)
        self.cls_model_dir = os.path.join(self.model_dir, "cls")
        os.makedirs(self.cls_model_dir, exist_ok=True)
        self.det_model_dir = os.path.join(self.model_dir, "det")
        os.makedirs(self.det_model_dir, exist_ok=True)
        self.rec_model_dir = os.path.join(self.model_dir, "rec")
        os.makedirs(self.rec_model_dir, exist_ok=True)
        self.ocr = PaddleOCR(
            lang="en",
            det_model_dir=self.det_model_dir,
            rec_model_dir=self.rec_model_dir,
            cls_model_dir=self.cls_model_dir,
        )

    def carregar_imagem_s3(self, bucket_name: str, key: str) -> np.ndarray:
        """
        Carrega uma imagem do S3 e a converte para um array numpy.

        Args:
            bucket_name (str): Nome do bucket S3.
            key (str): Chave do objeto no S3.

        Returns:
            np.ndarray: Imagem carregada como array numpy.
        """
        response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
        imagem_dados = response["Body"].read()
        imagem_np = np.frombuffer(imagem_dados, np.uint8)
        imagem = cv2.imdecode(imagem_np, cv2.IMREAD_COLOR)
        return imagem

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Pré-processa a imagem para normalização.

        Args:
            image (np.ndarray): Imagem a ser pré-processada.

        Returns:
            np.ndarray: Imagem pré-processada.
        """
        width = 320
        aspect_ratio = width / image.shape[1]
        new_height = int(image.shape[0] * aspect_ratio)
        image_resized = cv2.resize(image, (width, new_height))

        if new_height < 32:
            delta_h = 32 - new_height
            top, bottom = delta_h // 2, delta_h - (delta_h // 2)
            image_resized = cv2.copyMakeBorder(
                image_resized, top, bottom, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0]
            )
        else:
            image_resized = image_resized[:32, :]

        print(
            f"Forma da imagem normalizada antes da transposição: {image_resized.shape}"
        )
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_normalized = (image_resized.astype("float32") / 255.0 - mean) / std
        image_normalized = np.transpose(image_normalized, (2, 0, 1))
        print(
            f"Forma da imagem normalizada apos transposição: {image_normalized.shape}"
        )
        return image_normalized

    def save_metadata(self, bucket_name: str, image_key: str, unique_id: str) -> None:
        """
        Salva metadados no S3.

        Args:
            bucket_name (str): Nome do bucket S3.
            image_key (str): Chave do objeto no S3.
            unique_id (str): Identificador único para os metadados.

        Returns:
            None
        """
        metadata = {"timestamp": unique_id, "image_name": os.path.basename(image_key)}
        metadata_json = json.dumps(metadata)
        metadata_key = f"metadata/{os.path.basename(image_key)}.metadata.json"
        self.s3_client.put_object(
            Bucket=bucket_name,
            Key=metadata_key,
            Body=metadata_json,
            ContentType="application/json",
        )
        print(f"Metadata saved to S3: {metadata_key}")

    def save_image_data(
        self, image_key: str, image_path: str, plate_key: str, detected: int
    ) -> str:
        """
        Salva dados da imagem no DynamoDB.

        Args:
            image_key (str): Chave do objeto no S3.
            image_path (str): URL da imagem no S3.
            plate_key (str): Chave da imagem recortada da placa no S3.
            detected (int): Indica se uma placa foi detectada (1) ou não (0).

        Returns:
            str: Timestamp quando os dados foram salvos.
        """
        timestamp = datetime.utcnow().isoformat()
        self.table.put_item(
            Item={
                "PK": image_key,
                "timestamp": timestamp,
                "image_path": image_path,
                "cropped_image_path": plate_key,
                "detected": detected,
            }
        )
        return timestamp

    def process_image(self, bucket_name: str, metadata_key: str) -> None:
        """
        Processa a imagem para detectar placas e salvar resultados.

        Args:
            bucket_name (str): Nome do bucket S3.
            metadata_key (str): Chave do objeto de metadados no S3.

        Returns:
            None
        """
        response = self.s3_client.get_object(Bucket=bucket_name, Key=metadata_key)
        metadata_content = response["Body"].read().decode("utf-8")
        metadata = json.loads(metadata_content)

        uuid = metadata.get("timestamp")
        image_name = metadata.get("image_name")

        if not uuid or not image_name:
            print("Invalid metadata format. Missing 'uuid' or 'image_name'.")
            return

        print(f"UUID: {uuid}, Image Name: {image_name}")

        response = self.s3_client.get_object(Bucket=bucket_name, Key=image_name)
        plate_img = response["Body"].read()

        nparr = np.frombuffer(plate_img, np.uint8)
        imagem = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        print(f"Shape of the image: {imagem_rgb.shape}, dtype: {imagem_rgb.dtype}")

        try:
            resultados = self.ocr.ocr(imagem_rgb)
            print(f"Resultados do OCR: {resultados}")
        except Exception as e:
            print(f"Error during OCR: {str(e)}")
            return

        textos_detectados = []
        acuracias_detectadas = []
        if resultados:
            for linha in resultados:
                for item in linha:
                    if isinstance(item, list) and len(item) > 1:
                        box, (texto, acuracia) = item
                        texto_limpo = re.sub(r"[^a-zA-Z0-9]", "", texto)
                        textos_detectados.append(texto_limpo)
                        acuracias_detectadas.append(Decimal(str(acuracia)))
                    else:
                        print(f"Item inválido encontrado: {item}")

        type_plate = "type_plate_not_detect"
        error_type_plate = 0
        amount_characters = 0
        num_letters = 0
        num_numbers = 0

        if textos_detectados:
            for texto in textos_detectados:
                if re.match(r"^[A-Z]{3}\d{4}$", texto):
                    type_plate = "Mercosul"
                    error_type_plate = 1
                    break
                elif re.match(r"^[A-Z]{3}\d{1}[A-Z]{1}\d{2}$", texto):
                    type_plate = "Brazil"
                    error_type_plate = 1
                    break
                else:
                    num_letters = sum(c.isalpha() for c in texto)
                    num_numbers = sum(c.isdigit() for c in texto)
                    amount_characters = len(texto)

            print(f"Type_Plate: {type_plate}")
            print(f"Error Type Plate: {error_type_plate}")
            print(f"Number of Letters: {num_letters}")
            print(f"Number of Numbers: {num_numbers}")
            print(f"Amount of Characters: {amount_characters}")
            print("Textos detectados com confiança:")
            for texto, acuracia in zip(textos_detectados, acuracias_detectadas):
                print(f"Texto: {texto}, Acurácia: {acuracia}")
        else:
            print("Nenhum texto detectado.")

        if textos_detectados and acuracias_detectadas:
            self.table.update_item(
                Key={"PK": image_name, "timestamp": uuid},
                UpdateExpression="SET detected_text = :text, plate_accuracy = :accuracy, type_plate = :type_plate, error_type_plate = :error_type_plate, num_letters = :num_letters, num_numbers = :num_numbers, amount_characters = :amount_characters",
                ExpressionAttributeValues={
                    ":text": textos_detectados,
                    ":accuracy": acuracias_detectadas,
                    ":type_plate": type_plate,
                    ":error_type_plate": error_type_plate,
                    ":num_letters": num_letters,
                    ":num_numbers": num_numbers,
                    ":amount_characters": amount_characters,
                },
            )
            print(
                "OCR plate SAVED",
                image_name,
                uuid,
                textos_detectados,
                acuracias_detectadas,
                type_plate,
                error_type_plate,
                num_letters,
                num_numbers,
                amount_characters,
            )
        else:
            print("Nenhum texto ou acurácia para salvar no DynamoDB.")


def lambda_handler(event: dict, context: Optional[object]) -> None:
    """
    AWS Lambda handler function.

    Args:
        event (dict): The event data.
        context (Optional[object]): The context object.

    Returns:
        None
    """
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    metadata_key = event["Records"][0]["s3"]["object"]["key"]
    print("OCR plate triggered for ===: ", bucket_name, metadata_key)

    ocr_plate_detection = OCRPlateDetection()
    ocr_plate_detection.process_image(bucket_name, metadata_key)
