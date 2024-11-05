import os
import zipfile
import shutil


def	unzip_file(caminho, caminho_extracao):
	# Descompactar arquivos.

	for arquivo in arquivos:
		arquivos = os.listdir(caminho)
		if arquivo.endswith(".zip"):
			caminho_arquivo = os.path.join(caminho, arquivo)
			print(f"Extraindo {caminho_arquivo}...")
			with zipfile.ZipFile(caminho_arquivo, "r") as zip_ref:
				zip_ref.extractall(caminho_extracao)
			print(f"Extração concluída para {caminho_arquivo}")

def	path_created(unique_values, base_path):
	# Criar uma pasta para cada valor único da coluna
	for value in unique_values:
		pasta = os.path.join(base_path, value)  # Define o caminho da nova pasta
		os.makedirs(pasta, exist_ok=True)  # Cria a pasta se não existir
		print(f"Pasta '{pasta}' criada com sucesso!")

def	adjust_path(path, base_path):
	# Função para remover './' e unificar com o caminho base
	return base_path + path.lstrip('./')

def	create_txt_path(path, base_path):
	# Função para criar o caminho do arquivo .txt correspondente
	txt_path = path.replace('.jpg', '.txt')
	return base_path + txt_path.lstrip('./')

def	path_crated_list(unique_values, base_path):
	# Criar uma pasta para cada valor único da coluna
	for value in unique_values:
		for path in base_path:
			pasta = os.path.join(path, value)  # Define o caminho da nova pasta
			os.makedirs(pasta, exist_ok=True)  # Cria a pasta se não existir
			print(f"Pasta '{pasta}' criada com sucesso!")

def copy_files(row):

	image_file_name = os.path.basename(row['image_path'])
	txt_file_name = os.path.basename(row['txt_path'])

	new_image_path = os.path.join(row['move_path'], image_file_name)
	new_txt_path = os.path.join(row['move_path'], txt_file_name)

	os.makedirs(row['move_path'], exist_ok=True)

	# Copiar os arquivos
	shutil.move(row['image_path'], new_image_path)
	shutil.move(row['txt_path'], new_txt_path)

	print(f"Copied {row['image_path']} and {row['txt_path']} to {row['move_path']}")

	