import boto3
import streamlit as st
from botocore.exceptions import NoCredentialsError

class S3Interaction:
    """
    Classe responsável pela interação com o serviço S3 da AWS.
    """
    def __init__(self):
        """
        Inicializa o cliente S3 usando as credenciais armazenadas no Streamlit secrets.
        """
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=st.secrets["aws_access_key_id"],
            aws_secret_access_key=st.secrets["aws_secret_access_key"],
            region_name=st.secrets["aws_default_region"]
        )

    def upload_image(self, image, bucket_name, object_name=None):
        """
        Faz o upload de uma imagem para um bucket S3.

        Args:
            image (file): A imagem a ser enviada.
            bucket_name (str): O nome do bucket S3.
            object_name (str, optional): O nome do arquivo no S3. Se não for fornecido, o nome da imagem será utilizado.

        Returns:
            str: Mensagem indicando o resultado do upload.
        """
        if object_name is None:
            object_name = image.name

        try:
            self.s3_client.upload_fileobj(image, bucket_name, object_name)
            return f"Upload realizado com sucesso: {object_name}"
        except NoCredentialsError:
            return "Credenciais da AWS não encontradas."
        except Exception as e:
            return f"Ocorreu um erro: {str(e)}"