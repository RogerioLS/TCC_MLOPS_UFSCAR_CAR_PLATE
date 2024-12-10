FROM public.ecr.aws/lambda/python:3.10

# Atualizar pacotes e instalar dependências do sistema para OpenCV, PaddlePaddle, etc.
RUN yum update -y --setopt=timeout=300 --setopt=tries=5 && \
    yum install -y \
    gcc \
    gcc-c++ \
    gcc-gfortran \
    make \
    autoconf \
    automake \
    libtool \
    curl \
    wget \
    tar \
    libGL \
    libpng \
    libjpeg \
    libGL-devel \
    libpng-devel \
    libjpeg-devel \
    libtiff-devel \
    && yum clean all

# Atualizar pip para a versão mais recente
RUN pip install --upgrade pip

# dependências Python
RUN pip install --no-cache-dir boto3 opencv-python-headless paddlepaddle==2.4.2 paddleocr==2.9.1 numpy==1.26.3

ENV PADDLEOCR_MODEL_DIR="/tmp/.paddleocr"
ENV PATH="/usr/local/bin:${PATH}"

# diretório de trabalho
WORKDIR /var/task

# Copie o código da função Lambda para o diretório de trabalho
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Comando para executar a função Lambda
CMD ["lambda_function.lambda_handler"]
