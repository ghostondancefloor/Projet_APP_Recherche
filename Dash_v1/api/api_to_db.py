from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
import jwt
from datetime import datetime, timedelta
from typing import Dict , List, Optional

# MongoDB config
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["research_db_structure"]

# JWT config
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, limitez aux origines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(data: Dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "password":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token({"sub": form_data.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

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
