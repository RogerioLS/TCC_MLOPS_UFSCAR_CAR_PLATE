"""Módulo para tratamento de caminhos de arquivos."""

import os
import shutil
import zipfile


def unzip_file(caminho: str, caminho_extracao: str) -> None:
    """
    Descompacta arquivos zip em um diretório de extração.

    Args:
        caminho (str): Caminho para o diretório contendo os arquivos zip.
        caminho_extracao (str): Caminho para o diretório onde os arquivos serão extraídos.

    Returns:
        None
    """
    arquivos = os.listdir(caminho)
    for arquivo in arquivos:
        if arquivo.endswith(".zip"):
            caminho_arquivo = os.path.join(caminho, arquivo)
            print(f"Extraindo {caminho_arquivo}...")
            with zipfile.ZipFile(caminho_arquivo, "r") as zip_ref:
                zip_ref.extractall(caminho_extracao)
            print(f"Extração concluída para {caminho_arquivo}")


def path_created(unique_values: list, base_path: str) -> None:
    """
    Cria uma pasta para cada valor único da lista.

    Args:
        unique_values (list): Lista de valores únicos.
        base_path (str): Caminho base onde as pastas serão criadas.

    Returns:
        None
    """
    for value in unique_values:
        pasta = os.path.join(base_path, value)  # Define o caminho da nova pasta
        os.makedirs(pasta, exist_ok=True)  # Cria a pasta se não existir
        print(f"Pasta '{pasta}' criada com sucesso!")


def adjust_path(path: str, base_path: str) -> str:
    """
    Remove './' do caminho e unifica com o caminho base.

    Args:
        path (str): Caminho original.
        base_path (str): Caminho base.

    Returns:
        str: Caminho ajustado.
    """
    return base_path + path.lstrip("./")


def create_txt_path(path: str, base_path: str) -> str:
    """
    Cria o caminho do arquivo .txt correspondente ao arquivo de imagem.

    Args:
        path (str): Caminho do arquivo de imagem.
        base_path (str): Caminho base.

    Returns:
        str: Caminho do arquivo .txt correspondente.
    """
    txt_path = path.replace(".jpg", ".txt")
    return base_path + txt_path.lstrip("./")


def path_crated_list(unique_values: list, base_path: list) -> None:
    """
    Cria uma pasta para cada valor único da lista em múltiplos caminhos base.

    Args:
        unique_values (list): Lista de valores únicos.
        base_path (list): Lista de caminhos base onde as pastas serão criadas.

    Returns:
        None
    """
    for value in unique_values:
        for path in base_path:
            pasta = os.path.join(path, value)  # Define o caminho da nova pasta
            os.makedirs(pasta, exist_ok=True)  # Cria a pasta se não existir
            print(f"Pasta '{pasta}' criada com sucesso!")


def copy_files(row: dict) -> None:
    """
    Copia arquivos de imagem e texto para um novo diretório.

    Args:
        row (dict): Dicionário contendo os caminhos dos arquivos e o caminho de destino.

    Returns:
        None
    """
    image_file_name = os.path.basename(row["image_path"])
    txt_file_name = os.path.basename(row["txt_path"])

    new_image_path = os.path.join(row["move_path"], image_file_name)
    new_txt_path = os.path.join(row["move_path"], txt_file_name)

    os.makedirs(row["move_path"], exist_ok=True)

    # Copiar os arquivos
    shutil.move(row["image_path"], new_image_path)
    shutil.move(row["txt_path"], new_txt_path)

    print(f"Copied {row['image_path']} and {row['txt_path']} to {row['move_path']}")
