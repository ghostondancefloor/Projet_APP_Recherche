# Utiliser une image officielle Python
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers locaux dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Lancer l'application Streamlit
CMD ["streamlit", "run", "dashboard_with_login.py", "--server.port=8501", "--server.address=0.0.0.0"]
