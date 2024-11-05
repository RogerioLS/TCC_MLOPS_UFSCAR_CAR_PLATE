import os
import cv2
import matplotlib.pyplot as plt

def	convert_to_yolo_format(corners, img_width, img_height):
	# corner coordinates
	x1, y1, x2, y2, x3, y3, x4, y4 = map(int, corners.replace(",", " ").split())

	# Calculate the center coordinates
	x_min = min(x1, x2, x3, x4)
	x_max = max(x1, x2, x3, x4)
	y_min = min(y1, y2, y3, y4)
	y_max = max(y1, y2, y3, y4)

	x_center = (x_min + x_max) / 2.0
	y_center = (y_min + y_max) / 2.0

	# Calculate the width and height
	width = x_max - x_min
	height = y_max - y_min

	# Normalize the values by the image dimensions
	x_center /= img_width
	y_center /= img_height
	width /= img_width
	height /= img_height

	yolo_format = f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"

	return yolo_format

def read_input_file(file_path):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	car_plate = lines[0].strip().split(": ")[1]
	layout = lines[2].strip().split(": ")[1]
	corners = lines[3].strip().split(": ")[1]

	return car_plate, layout, corners

def	process_files(input_directory, output_directory, img_width, img_height):

	for file_name in os.listdir(input_directory):
		if file_name.startswith("img_") and file_name.endswith(".txt"):
			input_file_path = os.path.join(input_directory, file_name)
			car_plate, layout, corners = read_input_file(input_file_path)
			yolo_label = convert_to_yolo_format(corners, img_width, img_height)

			output_file_name = file_name.replace("img_", "img_")
			output_file_path = os.path.join(output_directory, output_file_name)

			with open(output_file_path, 'w') as output_file:
				output_file.write(yolo_label + "\n")

			print(f"Processed {input_file_path} -> {output_file_path}")


def	validation_bbx_conversion(image_path):
	image = cv2.imread(image_path)

	# Dimensões da imagem
	height, width, _ = image.shape

	# Coordenadas YOLO (x_center, y_center, width, height) normalizadas
	x_center_norm = 0.487891
	y_center_norm = 0.217361
	box_width_norm = 0.049219
	box_height_norm = 0.076389

	# Converta as coordenadas para o formato da imagem
	x_center = int(x_center_norm * width)
	y_center = int(y_center_norm * height)
	box_width = int(box_width_norm * width)
	box_height = int(box_height_norm * height)

	# Calcular as coordenadas do canto superior esquerdo e inferior direito
	x1 = int(x_center - box_width / 2)
	y1 = int(y_center - box_height / 2)
	x2 = int(x_center + box_width / 2)
	y2 = int(y_center + box_height / 2)

	# Desenhar o bounding box na imagem
	cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

	# Mostrar a imagem com o bounding box
	plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
	plt.axis("off")
	plt.show()