import streamlit as st
from PIL import Image
from boto3.dynamodb.conditions import Key
import boto3
import time
from src.utils import display_image, get_bucket_name, upload_button_pressed
from src.s3_lambda_interaction import S3Interaction

# Configurações de tema e estilo
st.set_page_config(
    page_title="Reconhecimento de Placas de Carro",
    page_icon="🚗",
    #layout="wide",  # Tela cheia para aproveitar o espaço
    initial_sidebar_state="expanded",
)

def fetch_plate_data(dynamodb_table_name, plate_key, max_retries=20, delay=5):
    """
    Busca os dados no DynamoDB relacionados à placa do carro, com tentativas.

    Args:
        dynamodb_table_name: Nome da tabela no DynamoDB.
        plate_key: Chave da placa a ser consultada.
        max_retries: Número máximo de tentativas.
        delay: Tempo de espera entre tentativas.

    Returns:
        Dados da placa ou mensagem de erro.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(dynamodb_table_name)

    for attempt in range(max_retries):
        try:
            # Consultar no DynamoDB
            response = table.query(
                KeyConditionExpression=Key("PK").eq(plate_key)
            )
            if response["Items"]:
                return response["Items"][0]  # Retorna o primeiro item encontrado
        except Exception as e:
            st.warning(f"Tentativa {attempt + 1}/{max_retries}: Dados não encontrados ainda. Retentando...")
            time.sleep(delay)

    return None  # Dados não encontrados após as tentativas

def main():
    """
    Função principal que define a interface do usuário
    e controla o fluxo de upload da imagem.
    """
    # Inicializa a aplicação Streamlit
    st.title("Reconhecimento de Placas de Carro")
    
    # Menu lateral personalizado
    st.sidebar.markdown('### Sobre o Projeto 🚗')
    st.sidebar.markdown(
        """
        Este projeto foi desenvolvido como parte de um TCC para a detecção automática de placas de carro. 
        A aplicação utiliza **YOLO** para detectar as placas e **OCR** para reconhecer os caracteres.
        
        ### Propósito
        Automatizar o processo de reconhecimento de placas de veículos para aplicações de controle de acesso, monitoramento, 
        e segurança veicular.

        ### Desenvolvedores
        - [Rogério Lopes](https://www.linkedin.com/in/seulinkedin)  
        - [Fabiana](https://www.linkedin.com/in/seulinkedin)
        
        ### Contatos
        - GitHub: [https://github.com/seugithub](https://github.com/seugithub)
        - LinkedIn: [https://linkedin.com/in/seulinkedin](https://linkedin.com/in/seulinkedin)
        """
    )

    st.write("Carregue uma imagem para reconhecer a placa do carro.")

    # Upload de imagem
    uploaded_image = st.file_uploader("Escolha uma imagem para upload", type=["jpg", "jpeg", "png"])

    # Verifica se uma imagem foi carregada
    if uploaded_image is not None:
        display_image(uploaded_image)
        bucket_name = "upload-image-first-stage-prod"  # Nome do bucket no S3
        dynamodb_table_name = "plate-detection-info-prod"  # Nome da tabela no DynamoDB

        # Confirmação do usuário
        confirm = st.checkbox("Você confirma que a imagem contém uma placa?")
        if confirm:
            st.success("Imagem confirmada! Você pode fazer o upload.")

            # Botão para realizar o upload
            if st.button("Fazer Upload"):
                s3_interaction = S3Interaction()

                # Criar um nome único para o objeto no S3 (usando o nome do arquivo)
                object_name = uploaded_image.name
                result_message = s3_interaction.upload_image(uploaded_image, bucket_name, object_name)
                st.success(result_message)

                # Simular a chave da placa (a chave deve ser gerada pela lógica do seu projeto)
                plate_key = object_name  # Neste caso, estamos usando o nome do arquivo como chave

                st.info("Buscando informações no DynamoDB...")

                # Buscar dados no DynamoDB
                plate_data = fetch_plate_data(dynamodb_table_name, plate_key)

                if plate_data:
                    st.success("Dados encontrados no DynamoDB:")
                    # Exibindo todos os dados do registro da placa
                    st.json(plate_data)

                    # Exibindo detalhes específicos dos atributos encontrados
                    st.write("**Cropped Image Path**: ", plate_data.get("cropped_image_path"))
                    st.write("**Detected**: ", plate_data.get("detected"))
                    st.write("**Detected Text**: ", plate_data.get("detected_text"))
                    st.write("**Image Path**: ", plate_data.get("image_path"))
                else:
                    st.error("Não foi possível encontrar informações relacionadas à placa.")

if __name__ == "__main__":
    main()
