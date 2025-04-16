FROM mongo:latest

# Copier les fichiers JSON dans /data
COPY *.json /data/

# Copier le script d'import
COPY import.sh /docker-entrypoint-initdb.d/import.sh

# Rendre le script exécutable
RUN chmod +x /docker-entrypoint-initdb.d/import.sh
