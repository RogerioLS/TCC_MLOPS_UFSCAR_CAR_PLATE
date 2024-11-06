import streamlit as st
from src.utils import display_image, get_bucket_name, upload_button_pressed
from src.s3_lambda_interaction import S3Interaction

# Configurações de tema e estilo
st.set_page_config(
    page_title="Reconhecimento de Placas de Carro",
    page_icon="🚗",
    layout="wide",  # Tela cheia para aproveitar o espaço
    initial_sidebar_state="expanded",
)

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

    # Verifica se uma imagem foi carregada e processa o upload para o bucket S3
    if uploaded_image is not None:
        display_image(uploaded_image)
        bucket_name = "teste-imagem-2"  # Nome do bucket no S3

        if upload_button_pressed():
            s3_interaction = S3Interaction()
            result_message = s3_interaction.upload_image(uploaded_image, bucket_name)
            st.success(result_message)

if __name__ == "__main__":
    main()