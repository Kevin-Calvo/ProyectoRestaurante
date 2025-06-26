# Usar Node.js como imagen base
FROM node:18

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY package.json package-lock.json ./
RUN npm install

# Copiar el resto del código fuente
COPY . .

# Exponer el puerto de la API
EXPOSE 3000

# Comando para ejecutar la API
CMD ["node", "index.js"]
 
