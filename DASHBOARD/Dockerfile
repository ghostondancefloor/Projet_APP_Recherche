# Utilise une image officielle Python comme image de base
FROM python:3.10

# Créer un dossier dans le conteneur
WORKDIR /app

# Copier tous les fichiers du projet dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Commande pour lancer le dashboard
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
