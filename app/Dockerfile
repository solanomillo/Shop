#imagen original
FROM python:3.11.0-alpine

#set work directory
WORKDIR /usr/src/app

#configurar variables entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias para mysqlclient y otros paquetes
RUN apk add --update --no-cache mariadb-connector-c-dev \
    && apk add --no-cache --virtual .build-deps \
    mariadb-dev \
    gcc \
    musl-dev \
    && pip install --no-cache-dir mysqlclient>=1.4.3 \
    && apk del .build-deps \
    && apk add libffi-dev openssl-dev libgcc

# Instalar dependencias de python
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copiar el proyecto
COPY . .

# Ejecutar Django
CMD python manage.py runserver

EXPOSE 8000
