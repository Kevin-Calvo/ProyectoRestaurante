# Imagen base de Node.js
FROM node:18

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivos del microservicio
COPY . .

# Instalar dependencias
RUN npm install

# Exponer el puerto en el que corre el microservicio
EXPOSE 4000

# Comando para ejecutar la app
CMD ["node", "index.js"]
