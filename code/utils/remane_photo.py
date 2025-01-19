"""Módulo para renomear fotos em uma pasta específica."""

import os

from google.colab import drive

# Caminho para a pasta de imagens
folder_path = "/content/drive/MyDrive/ColabNotebooks/tcc_mba/detectando_placa_opecv/placas_exemplos_para_deteccao"


def rename_photos(folder_path: str) -> None:
    """
    Renomeia os arquivos de imagem na pasta especificada.

    Args:
        folder_path (str): Caminho para a pasta contendo as imagens.

    Returns:
        None
    """
    # Obtém a lista de arquivos na pasta
    files = os.listdir(folder_path)

    # Renomeia os arquivos
    for i, filename in enumerate(files):
        new_name = f"placa_{i+1}.jpg"

        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_name)

        os.rename(old_file, new_file)

        print(f"{filename} renomeado para {new_name}")
