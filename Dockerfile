# Utilizar una imagen base de Python
FROM python:3.9-alpine

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar los archivos de requerimientos al contenedor
COPY requirements.txt ./

# Instalar las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos del proyecto al contenedor
COPY . .

# Exponer el puerto en el que Flask correrá
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]