from src import boto3
from src import BytesIO

class S3Interaction:
    def __init__(self):
        self.s3_client = boto3.client("s3")

    def upload_image(self, image_buffer: BytesIO, bucket_name: str, object_name: str) -> str:
        """
        Faz upload da imagem para o bucket S3.

        Args:
            image_buffer (BytesIO): Buffer da imagem a ser enviada.
            bucket_name (str): Nome do bucket S3.
            object_name (str): Nome do objeto no S3.

        Returns:
            str: Mensagem de sucesso com o nome do objeto.
        """
        try:
            image_buffer.seek(0)
            self.s3_client.upload_fileobj(image_buffer, bucket_name, object_name)
            return f"Upload realizado com sucesso: {object_name}"
        except Exception as e:
            return f"Erro ao fazer upload: {str(e)}"
