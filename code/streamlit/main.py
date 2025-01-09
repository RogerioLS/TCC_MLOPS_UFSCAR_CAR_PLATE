import time
from io import BytesIO
import boto3
from PIL import Image
import streamlit as st

class S3Interaction:
    def __init__(self):
        self.s3_client = boto3.client("s3")

    def upload_image(self, image_buffer, bucket_name, object_name):
        """
        Faz upload da imagem para o bucket S3.

        Args:
            image_buffer: Buffer da imagem a ser enviada.
            bucket_name: Nome do bucket S3.
            object_name: Nome do objeto no S3.

        Returns:
            Mensagem de sucesso com o nome do objeto.
        """
        try:
            image_buffer.seek(0)
            self.s3_client.upload_fileobj(image_buffer, bucket_name, object_name)
            return f"Upload realizado com sucesso: {object_name}"
        except Exception as e:
            return f"Erro ao fazer upload: {str(e)}"

def fetch_plate_data(dynamodb_table_name, object_name, max_retries=20, delay=10):
    """
    Busca informações da placa no DynamoDB com base no nome do objeto.

    Args:
        dynamodb_table_name: Nome da tabela no DynamoDB.
        object_name: Nome do objeto correspondente no S3.
        max_retries: Número máximo de tentativas de busca.
        delay: Tempo de espera entre as tentativas (em segundos).

    Returns:
        Dados da placa ou None, se não encontrado.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(dynamodb_table_name)

    for attempt in range(max_retries):
        try:
            response = table.scan()
            items = response.get("Items", [])

            # Busca o registro mais recente com o nome do objeto
            matching_items = [item for item in items if item.get("PK") == object_name]
            if matching_items:
                return max(matching_items, key=lambda x: x.get("timestamp", 0))

            st.info(f"Tentativa {attempt + 1}/{max_retries}: Dados não encontrados, aguardando {delay} segundos...")
            time.sleep(delay)  # Aguarda antes de tentar novamente
        except Exception as e:
            st.error(f"Erro ao buscar dados no DynamoDB: {str(e)}")
            return None

    st.error("Tempo de espera esgotado. Não foi possível encontrar informações relacionadas à placa.")
    return None

def display_results(original_image_buffer, plate_data):
    """
    Exibe os resultados da detecção na interface do usuário.

    Args:
        original_image_buffer: Buffer de imagem original.
        plate_data: Dados da placa encontrados no DynamoDB.
    """
    col1, col2 = st.columns(2)

    # Rewind buffer para reutilização
    original_image_buffer.seek(0)
    original_image = Image.open(original_image_buffer)

    # Exibe a imagem original
    with col1:
        st.image(original_image, caption="Imagem Original", use_column_width=True)

    # Exibe os resultados do DynamoDB
    with col2:
        if plate_data:
            if plate_data.get("detected") == 0:
                st.warning("Nenhuma placa detectada na imagem.")
                return
            st.success("Dados encontrados no DynamoDB:")
            st.write("**Cropped Image Path:** ", plate_data.get("cropped_image_path"))
            st.write("**Detected:** ", plate_data.get("detected"))
            st.write("**Detected Text:** ", plate_data.get("detected_text"))
            st.write("**Image Path:** ", plate_data.get("image_path"))
            # Exibe a imagem recortada da placa, se disponível
            cropped_image_path = plate_data.get("cropped_image_path")
            if cropped_image_path:
                st.image(cropped_image_path, caption="Placa Detectada", use_column_width=True)
        else:
            st.error("Não foi possível encontrar informações relacionadas à placa.")

def main():
    st.title("Reconhecimento de Placas")

    # Upload de múltiplas imagens pelo usuário
    uploaded_images = st.file_uploader("Carregue uma ou mais imagens", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_images:
        # Configurações do S3 e DynamoDB
        bucket_name = "upload-image-first-stage-prod"
        dynamodb_table_name = "plate-detection-info-prod"

        # Confirmação do usuário
        confirm = st.checkbox("Você confirma que as imagens contêm placas?")
        if confirm:
            st.success("Imagens confirmadas! Você pode fazer o upload.")

            # Botão para realizar o upload
            if st.button("Fazer Upload"):
                s3_interaction = S3Interaction()

                for uploaded_image in uploaded_images:
                    # Mantém os dados da imagem em um buffer
                    uploaded_image_buffer = BytesIO(uploaded_image.read())
                    uploaded_image_buffer.seek(0)

                    # Cria uma cópia do buffer para evitar fechamento prematuro
                    image_buffer_copy = BytesIO(uploaded_image_buffer.getvalue())

                    # Exibe a imagem original carregada
                    st.subheader(f"Imagem carregada: {uploaded_image.name}")
                    st.image(image_buffer_copy, caption="Imagem Original", use_column_width=True)

                    # Criar um nome único para o objeto no S3
                    object_name = f"{time.time_ns()}_{uploaded_image.name}"
                    result_message = s3_interaction.upload_image(uploaded_image_buffer, bucket_name, object_name)
                    st.success(result_message)

                    # Busca no DynamoDB
                    st.info(f"Aguardando informações no DynamoDB para {uploaded_image.name}...")
                    plate_data = fetch_plate_data(dynamodb_table_name, object_name)

                    # Reposiciona o buffer da imagem antes de reutilizá-lo
                    image_buffer_copy.seek(0)
                    # Exibe resultados
                    display_results(image_buffer_copy, plate_data)

if __name__ == "__main__":
    main()