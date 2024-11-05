import os
import shutil
import random

def organizar_amostras(base_dir, dest_dir_base, categories, total_train, total_val, total_test):
	# Função para organizar as amostras por categoria
	quantidades_desejadas = {
		'train': total_train // len(categories),
		'val': total_val // len(categories),
		'test': total_test // len(categories)
	}

	# Criar as pastas de destino
	for tipo in ['train', 'val', 'test']:
		os.makedirs(os.path.join(dest_dir_base, tipo, 'images'), exist_ok=True)
		os.makedirs(os.path.join(dest_dir_base, tipo, 'labels'), exist_ok=True)

	for category in categories:
		imagens = [f for f in os.listdir(os.path.join(base_dir, category)) if f.endswith('.jpg')]

		# Verificar se há imagens suficientes
		if len(imagens) < quantidades_desejadas['train']:
			print(f"Categoria '{category}' não possui amostras suficientes para treino. Utilizando o máximo disponível ({len(imagens)} amostras).")
			quantidades_desejadas['train'] = len(imagens)

		# Embaralhar as imagens
		random.shuffle(imagens)

		# Copiar as amostras para as pastas de treino, validação e teste
		for tipo in ['train', 'val', 'test']:
			# Determinar quantas amostras copiar
			num_samples = quantidades_desejadas[tipo]
			for i in range(num_samples):
				if i < len(imagens):
					# Copiar imagem
					src_image = os.path.join(base_dir, category, imagens[i])
					dest_image = os.path.join(dest_dir_base, tipo, 'images', imagens[i])
					shutil.copy(src_image, dest_image)

					# Copiar label correspondente
					src_label = os.path.join(base_dir, category, imagens[i].replace('.jpg', '.txt'))
					dest_label = os.path.join(dest_dir_base, tipo, 'labels', imagens[i].replace('.jpg', '.txt'))
					shutil.copy(src_label, dest_label)

		# Print para verificar o número de amostras copiadas
		print(f"Categoria '{category}': {quantidades_desejadas['train']} amostras para treino, {quantidades_desejadas['val']} amostras para validação, {quantidades_desejadas['test']} amostras para teste.")