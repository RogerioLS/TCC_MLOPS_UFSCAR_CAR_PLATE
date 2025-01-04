import boto3
import cv2
import os
import numpy as np
import json
from paddleocr import PaddleOCR

# Configurações do AWS S3 e DynamoDB
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('plate-detection-info-dev')

# Definir o diretório de modelos como /tmp para PaddleOCR
model_dir = "/tmp/.paddleocr"
os.makedirs(model_dir, exist_ok=True)

# Criar diretório para o modelo de classificação
cls_model_dir = os.path.join(model_dir, "cls")
os.makedirs(cls_model_dir, exist_ok=True)

det_model_dir = os.path.join(model_dir, "det")
os.makedirs(det_model_dir, exist_ok=True)

rec_model_dir = os.path.join(model_dir, "rec")
os.makedirs(rec_model_dir, exist_ok=True)

# Inicializar o PaddleOCR com os diretórios dos modelos
ocr = PaddleOCR(lang='en', det_model_dir=det_model_dir, rec_model_dir=rec_model_dir, cls_model_dir=cls_model_dir)
#use_angle_cls=True

#ocr = PaddleOCR(lang='en')

# Função para carregar imagem do S3
def carregar_imagem_s3(bucket_name, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=key)
    imagem_dados = response['Body'].read()

    # Converter os dados da imagem em um array numpy
    imagem_np = np.frombuffer(imagem_dados, np.uint8)
    imagem = cv2.imdecode(imagem_np, cv2.IMREAD_COLOR)

    return imagem



def preprocess_image(image):

    # Redimensiona a imagem para largura 320 mantendo a proporção
    width = 320
    aspect_ratio = width / image.shape[1]
    new_height = int(image.shape[0] * aspect_ratio)
    image_resized = cv2.resize(image, (width, new_height))

    # Ajusta para altura de 32 (preenchendo ou cortando)
    if new_height < 32:
        delta_h = 32 - new_height
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        image_resized = cv2.copyMakeBorder(image_resized, top, bottom, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    else:
        image_resized = image_resized[:32, :]

    print(f"Forma da imagem normalizada antes da transposição: {image_resized.shape}")
    # Normalização no formato HWC as in paddle dected config
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image_normalized = (image_resized.astype('float32') / 255.0 - mean) / std

    # Transpõe para o formato CHW, como o modelo espera
    image_normalized = np.transpose(image_normalized, (2, 0, 1))
    
    print(f"Forma da imagem normalizada apos transposição: {image_normalized.shape}")
    return image_normalized

def lambda_handler(event, context):
    # Extrair informações do evento
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    metadata_key = event['Records'][0]['s3']['object']['key']
    print("OCR plate triggered for ===: ", bucket_name, metadata_key)

    # Obter o arquivo de metadata do S3
    response = s3_client.get_object(Bucket=bucket_name, Key=metadata_key)
    metadata_content = response['Body'].read().decode('utf-8')
    metadata = json.loads(metadata_content)

    # Extrair UUID e nome da imagem do metadata
    uuid = metadata.get('timestamp')
    image_name = metadata.get('image_name')

    if not uuid or not image_name:
        print("Invalid metadata format. Missing 'uuid' or 'image_name'.")
        return

    print(f"UUID: {uuid}, Image Name: {image_name}")

    # Obter a imagem do S3
    response = s3_client.get_object(Bucket=bucket_name, Key=image_name)
    plate_img = response['Body'].read()

    nparr = np.frombuffer(plate_img,np.uint8)
    imagem = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

    # Verificar a forma da imagem
    altura, largura, _ = imagem_rgb.shape
    print(f"Shape of the image: {imagem_rgb.shape}, dtype: {imagem_rgb.dtype}")

    # Executar OCR na imagem
    try:
        resultados = ocr.ocr(imagem_rgb)
        print(f"Resultados do OCR: {resultados}")
    except Exception as e:
        print(f"Error during OCR: {str(e)}")
        return

    # Extrair e exibir o texto detectado
    textos_detectados = []
    if (any(resultados)):  # Verifique se há resultados
        for linha in resultados:
            for item in linha:
                if isinstance(item, list) and len(item) > 1:
                    box, (texto, *confidencia) = item
                    conf = confidencia[0] if confidencia else None  # Confiança pode não estar presente
                    textos_detectados.append((texto))
                else:
                    print(f"Item inválido encontrado: {item}")

    if textos_detectados:
        print("Textos detectados com confiança:")
        for texto in textos_detectados:
           print(f"Texto: {texto}")
    else:
        print("Nenhum texto detectado.")

    # Atualizar o DynamoDB com o texto detectado
    if textos_detectados:  # Atualizar apenas se houver textos detectados
        table.update_item(
            Key={
                'PK': image_name,
                'timestamp': uuid
            },
            UpdateExpression="SET detected_text = :text",
            ExpressionAttributeValues={':text': textos_detectados}
        )
        print("OCR plate SAVED", image_name, uuid, textos_detectados)
    else:
        print("Nenhum texto para salvar no DynamoDB.")
