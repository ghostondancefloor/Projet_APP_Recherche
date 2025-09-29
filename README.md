# Projet_APP_Recherche

## ⚙️ Setting up the Python Virtual Environment

Follow these steps to set up and use the virtual environment for this project.

### 1. Clone the Repository

```bash
git clone git@github.com:ghostondancefloor/Projet_APP_Recherche.git
```

If Python is not installed, you can download it from the official site:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

### 2. Create a Virtual Environment

Navigate to the root of the project and run:

```bash
python -m venv venv
```

This creates a `venv/` directory with an isolated Python environment.

### 3. Activate the Virtual Environment

**Windows:**

```bash
.\venv\Scripts\activate
```

**MacOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Install Project Dependencies

Make sure the environment is activated, then run:

```bash
pip install -r requirements.txt
```

### 5. Deactivate When Finished

```bash
deactivate
```

### 6. (Optional) Update Requirements File

Freeze current dependencies into `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

## 🧪 Setting up the MongoDB Research Database

This guide explains how to run the `research_db_structure` MongoDB image and import the provided data into the container.

### 📦 What You Need

- [Docker](https://www.docker.com/products/docker-desktop) installed
- Docker Hub access to pull the image: `danlimao/research_db_structure:v2`
- Extracted `.rar` file containing the MongoDB dump (e.g., to `C:\mongo-dump`)

---

### 🚀 MongoDB Setup Steps

#### 1. Create a `docker-compose.yml`

```yaml
version: "3.8"
services:
  mongodb:
    image: danlimao/research_db_structure:v2
    container_name: research_db_container
    ports:
      - "27017:27017"
    volumes: []
```

Save this in your project directory.

#### 2. Start the MongoDB Container

```bash
docker-compose up -d
```

#### 3. Extract the MongoDB Dump

Unpack the `.rar` file you received (e.g., to `C:\mongo-dump`). Ensure the structure looks like:

```
/mongo-dump/research_db_structure/collection1.bson
```

#### 4. Copy Dump Files into the Container

```bash
docker cp C:\mongo-dump research_db_container:/dump
docker cp C:\Users\ikram\OneDrive\Desktop\Projet_APP_Recherche\Dash_MONGODB\mongo-dump research_db_container:/dump
```

#### 5. Restore the Database from Dump

```bash
docker exec -it research_db_container mongorestore /dump
```

#### 6. Verify Data Import (Optional)

```bash
docker exec -it research_db_container mongosh
```

Then inside `mongosh`:

```javascript
show dbs
use research_db_structure
show collections
```

You should see collections like `chercheurs`, `institutions`, etc.

---

## ✅ You're All Set!

Your environment and MongoDB container are now ready. You can connect to MongoDB via `mongosh`, MongoDB Compass, or any client at `localhost:
