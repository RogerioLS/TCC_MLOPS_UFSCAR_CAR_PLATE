FROM public.ecr.aws/lambda/python:3.10

# Diretório onde o código e arquivos serão copiados
WORKDIR /var/task
RUN yum install -y libGL libGL-devel

# Dependências necessárias
RUN pip install opencv-python-headless numpy torch torchvision Pillow boto3 ultralytics

# Copie o código da função Lambda para o diretório de trabalho
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Copie o modelo treinado para o diretório de trabalho
COPY yolov8_model.pt ${LAMBDA_TASK_ROOT}

# Comando para executar a função Lambda
CMD ["lambda_function.lambda_handler"]
