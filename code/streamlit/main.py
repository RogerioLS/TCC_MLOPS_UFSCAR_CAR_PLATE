"""Módulo principal para a aplicação de reconhecimento de placas de carro."""

from src import Any, BytesIO, Dict, DynamoDBInteraction, Image, S3Interaction, st, time

# Configurações de tema e estilo
st.set_page_config(
    page_title="Reconhecimento de Placas de Carro",
    page_icon="🚗",
    initial_sidebar_state="expanded",
)


def display_results(original_image_buffer: BytesIO, plate_data: Dict[str, Any]) -> None:
    """
    Exibe os resultados da detecção na interface do usuário.

    Args:
        original_image_buffer (BytesIO): Buffer de imagem original.
        plate_data (Dict[str, Any]): Dados da placa encontrados no DynamoDB.
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
                st.image(
                    cropped_image_path, caption="Placa Detectada", use_column_width=True
                )
        else:
            st.error("Não foi possível encontrar informações relacionadas à placa.")


def main() -> None:
    """
    Função principal que define a interface do usuário e controla o fluxo de upload da imagem.

    Inicializa a aplicação Streamlit, configura o menu lateral e gerencia o upload de imagens pelo usuário.
    """
    # Inicializa a aplicação Streamlit
    st.title("Reconhecimento de Placas de Carro")

    # Menu lateral personalizado
    st.sidebar.markdown("### Sobre o Projeto 🚗")
    st.sidebar.markdown(
        """
        Este projeto foi desenvolvido como parte de um TCC para a detecção automática de placas de carro.
        A aplicação utiliza **YOLO** para detectar as placas e **OCR** para reconhecer os caracteres.

        ### Propósito
        Automatizar o processo de reconhecimento de placas de veículos para aplicações de controle de acesso, monitoramento,
        e segurança veicular.

        ### Desenvolvedores
        - [Rogério Lopes](https://www.linkedin.com/in/rogerio-lopes-57627615b/)
        - [Fabiana Florentin](https://www.linkedin.com/in/fabiana-f-530a495/)

        ### Repositório
        - [GitHub](https://github.com/RogerioLS/TCC_MLOPS_UFSCAR_CAR_PLATE)
        """
    )
    # Upload de múltiplas imagens pelo usuário
    uploaded_images = st.file_uploader(
        "Carregue uma ou mais imagens",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )

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
                dynamodb_interaction = DynamoDBInteraction()

                for uploaded_image in uploaded_images:
                    # Mantém os dados da imagem em um buffer
                    uploaded_image_buffer = BytesIO(uploaded_image.read())
                    uploaded_image_buffer.seek(0)

                    # Cria uma cópia do buffer para evitar fechamento prematuro
                    image_buffer_copy = BytesIO(uploaded_image_buffer.getvalue())

                    # Exibe a imagem original carregada
                    st.subheader(f"Imagem carregada: {uploaded_image.name}")
                    st.image(
                        image_buffer_copy,
                        caption="Imagem Original",
                        use_column_width=True,
                    )

                    # Criar um nome único para o objeto no S3
                    object_name = f"{time.time_ns()}_{uploaded_image.name}"
                    result_message = s3_interaction.upload_image(
                        uploaded_image_buffer, bucket_name, object_name
                    )
                    st.success(result_message)

                    # Busca no DynamoDB
                    st.info(
                        f"Aguardando informações no DynamoDB para {uploaded_image.name}..."
                    )
                    plate_data = dynamodb_interaction.fetch_plate_data(
                        dynamodb_table_name, object_name
                    )

                    # Verifica se a placa foi detectada
                    if plate_data and plate_data.get("detected") == 0:
                        st.warning(
                            f"Nenhuma placa detectada na imagem {uploaded_image.name}. Pulando para a próxima imagem."
                        )
                        continue

                    # Reposiciona o buffer da imagem antes de reutilizá-lo
                    image_buffer_copy.seek(0)
                    # Exibe resultados
                    display_results(image_buffer_copy, plate_data)


if __name__ == "__main__":
    main()
