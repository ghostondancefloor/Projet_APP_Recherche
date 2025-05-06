# Utiliser une image officielle Python légère
FROM python:3.10-slim

# Définir le dossier de travail à /app dans le conteneur
WORKDIR /app

# Copier tous les fichiers du dossier local (viz/) dans /app
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Ouvrir le port 8501 (utilisé par Streamlit)
EXPOSE 8501

# Démarrer Streamlit
CMD ["streamlit", "run", "dashboard_with_login.py", "--server.port=8501", "--server.address=0.0.0.0"]
