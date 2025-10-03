from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from passlib.context import CryptContext
from bson.objectid import ObjectId

# MongoDB config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/research_db_structure")
client = AsyncIOMotorClient(MONGO_URI)

# Log de débogage pour l'URI MongoDB
print(f"Connecting to MongoDB at: {MONGO_URI}")
db = client["research_db_structure"]

# JWT config - read from environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Configuration de l'encryption des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, limitez aux origines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Event handler for application startup
@app.on_event("startup")
async def startup_db_client():
    try:
        # Test if we can connect to MongoDB
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Check if users collection exists and count documents
        users_count = await db.users.count_documents({})
        print(f"Found {users_count} users in database")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

# Fonction pour vérifier les mots de passe hachés
def verify_password(plain_password, hashed_password):
    print(f"Verifying password: {plain_password[:2]}*** against hash: {hashed_password[:10]}***")
    is_verified = pwd_context.verify(plain_password, hashed_password)
    print(f"Password verification result: {is_verified}")
    return is_verified

# Fonction pour obtenir un utilisateur depuis la base de données
async def get_user(username: str):
    print(f"Looking for user: {username}")
    # Note: Using db.users - make sure this collection exists
    user = await db.users.find_one({"username": username})
    if user:
        print(f"User found: {username}")
    else:
        print(f"User not found: {username}")
    return user

# Fonction pour authentifier un utilisateur
async def authenticate_user(username: str, password: str):
    print(f"Attempting to authenticate user: {username}")
    user = await get_user(username)
    if not user:
        print(f"User {username} not found in database")
        return False
    if not verify_password(password, user["password"]):
        print(f"Password verification failed for user {username}")
        return False
    print(f"Authentication successful for user {username}")
    return user

def create_access_token(data: Dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Login attempt for username: {form_data.username}")
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        print(f"Authentication failed for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Conversion ObjectId en string pour le JSON
    user_id = str(user["_id"]) if "_id" in user else None
    
    access_token = create_access_token(
        data={"sub": form_data.username, "id": user_id}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    print(f"Token created for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token d'authentification invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Vérifier que l'utilisateur existe toujours dans la base de données
        user = await get_user(username)
        if user is None:
            raise credentials_exception
            
        return payload
    except jwt.PyJWTError:
        raise credentials_exception

@app.get("/api/chercheurs", response_model=List[Dict])
async def get_chercheurs(token: dict = Depends(verify_token)):
    cursor = db.chercheurs.find({}, {"_id": 0})
    return [doc async for doc in cursor]

@app.get("/api/chercheurs/{nom}", response_model=Dict)
async def get_chercheur(nom: str, token: dict = Depends(verify_token)):
    doc = await db.chercheurs.find_one({"nom": nom}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Chercheur non trouvé")
    return doc

@app.get("/api/publications", response_model=List[Dict])
async def get_publications(token: dict = Depends(verify_token)):
    cursor = db.publications.find({}, {"_id": 0})
    return [doc async for doc in cursor]

@app.get("/api/stats_pays", response_model=List[Dict])
async def get_stats_pays(token: dict = Depends(verify_token)):
    cursor = db.stats_pays.find({}, {"_id": 0})
    return [doc async for doc in cursor]

@app.get("/api/institutions", response_model=List[Dict])
async def get_institutions(token: dict = Depends(verify_token)):
    cursor = db.institutions.find({}, {"_id": 0})
    return [doc async for doc in cursor]

@app.get("/api/collaborations", response_model=List[Dict])
async def get_collaborations(token: dict = Depends(verify_token)):
    cursor = db.collaborations.find({}, {"_id": 0})
    return [doc async for doc in cursor]

@app.get("/api/users", response_model=List[Dict])
async def get_users(token: dict = Depends(verify_token)):
    # Use correct collection path - users not research_db_structure.users since we already selected the database
    cursor = db.users.find({}, {"password": 0})
    users = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Convertir ObjectId en string
        users.append(doc)
    return users

@app.get("/api/me", response_model=Dict)
async def get_current_user(token: dict = Depends(verify_token)):
    username = token.get("sub")
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Ne pas renvoyer le mot de passe et convertir ObjectId en string
    user["_id"] = str(user["_id"])
    if "password" in user:
        del user["password"]
    
    return user

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API de recherche scientifique"}