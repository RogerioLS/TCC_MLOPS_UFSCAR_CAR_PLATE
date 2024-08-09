import streamlit as st
from src.utils import display_image, get_bucket_name, upload_button_pressed
from src.s3_lambda_interaction import S3Interaction


def main():
    """
    Função principal que define a interface do usuário
    e controla o fluxo de upload da imagem.
    """
    # Inicializa a aplicação Streamlit
    st.title("Reconhecimento de Placas de Carro")
    st.write("Carregue uma imagem para reconhecer a placa do carro.")

    uploaded_image = st.file_uploader("Escolha uma imagem para upload", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        display_image(uploaded_image)
        bucket_name = get_bucket_name()
        if upload_button_pressed():
            s3_interaction = S3Interaction()
            result_message = s3_interaction.upload_image(uploaded_image, bucket_name)
            st.success(result_message)

if __name__ == "__main__":
    main()
