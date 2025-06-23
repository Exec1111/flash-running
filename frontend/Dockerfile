FROM node:20

# Répertoire de travail
WORKDIR /app

# Copier uniquement les fichiers package pour installer les deps d'abord
COPY package*.json ./
RUN npm install --legacy-peer-deps --silent

# Copier le reste du code
COPY . /app

# Exposer le port Next.js
EXPOSE 3000

# Lancer le serveur de dev (pour prod on utilisera `next start` après build)
CMD ["npm", "run", "dev"]
