FROM python:3.10

WORKDIR /app

# Copier uniquement les fichiers nécessaires
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'API
COPY . .

# Lancer l'app FastAPI avec uvicorn
CMD ["uvicorn", "api_to_db:app", "--host", "0.0.0.0", "--port", "8000"]