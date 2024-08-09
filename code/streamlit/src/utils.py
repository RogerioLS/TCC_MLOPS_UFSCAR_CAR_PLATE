import streamlit as st

def display_image(image):
    """
    Exibe a imagem carregada no Streamlit.

    Args:
        image (file): A imagem a ser exibida.
    """
    st.image(image, caption="Imagem Carregada", use_column_width=True)

def get_bucket_name():
    """
    Cria um campo de entrada de texto para o nome do bucket S3.

    Returns:
        str: O nome do bucket inserido pelo usuário.
    """
    return st.text_input("test-tcc")

def upload_button_pressed():
    """
    Cria um botão para realizar o upload da imagem.

    Returns:
        bool: Verdadeiro se o botão for pressionado, falso caso contrário.
    """
    return st.button("Fazer Upload")
