import os
import shutil
import random

import os

# Defina os diretórios de origem
base_dir = '/content/drive/MyDrive/ColabNotebooks/tcc_mba/treinamento_yolo_placa/training'
categories = ['cars-br', 'cars-me', 'motorcycles-br', 'motorcycles-me']

# Função para organizar as amostras por categoria (sem exigir correspondência exata)
def quantidade_amostras():
    amostras_por_categoria = {category: {'imagens': 0, 'labels': 0} for category in categories}

    # Obter a contagem de todas as imagens e arquivos txt das categorias
    for category in categories:
        imagens = [f for f in os.listdir(os.path.join(base_dir, category)) if f.endswith('.jpg')]
        labels = [f for f in os.listdir(os.path.join(base_dir, category)) if f.endswith('.txt')]

        # Contar o total de imagens e labels
        amostras_por_categoria[category]['imagens'] = len(imagens)
        amostras_por_categoria[category]['labels'] = len(labels)

        # Print para verificar o número de amostras (imagens e labels) por categoria
        print(f"Categoria '{category}': {len(imagens)} imagens, {len(labels)} labels.")

    return amostras_por_categoria

# Defina os diretórios de origem e destino
base_dir = '/content/drive/MyDrive/ColabNotebooks/tcc_mba/treinamento_yolo_placa/training'
dest_dir_base = '/content/drive/MyDrive/ColabNotebooks/tcc_mba/treinamento_yolo_placa/training_800'
categories = ['cars-br', 'cars-me', 'motorcycles-br', 'motorcycles-me']

# Quantidades desejadas
total_train = 560
total_val = 160
total_test = 80

# Função para organizar as amostras por categoria
def organizar_amostras():
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