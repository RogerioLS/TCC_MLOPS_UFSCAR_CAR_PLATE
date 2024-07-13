import os

def convert_to_yolo_format(corners, img_width, img_height):
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

def process_files(input_directory, img_width, img_height):
    for file_name in os.listdir(input_directory):
        if file_name.startswith("img_") and file_name.endswith(".txt"):
            input_file_path = os.path.join(input_directory, file_name)
            car_plate, layout, corners = read_input_file(input_file_path)
            yolo_label = convert_to_yolo_format(corners, img_width, img_height)
            
            output_file_name = file_name.replace("img_", "img_yolo_")
            output_file_path = os.path.join(input_directory, output_file_name)
            
            with open(output_file_path, 'w') as output_file:
                output_file.write(yolo_label + "\n")
            
            print(f"Processed {input_file_path} -> {output_file_path}")

# Example usage
input_directory = './'  #  path that contains the images' labels txt
img_width = 1280  # image width
img_height = 720  # image height

process_files(input_directory, img_width, img_height)
