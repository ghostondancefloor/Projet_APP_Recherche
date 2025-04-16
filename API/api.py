from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
from datetime import datetime, timedelta
from typing import Dict

# MongoDB config
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["mydatabase"]
collection = db["data"]

# JWT config
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
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

@app.get("/data/{filename}")
async def get_data(filename: str, token: dict = Depends(verify_token)):
    doc = await collection.find_one({"filename": filename})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found in database")
    doc.pop("_id", None)  # remove Mongo's ObjectId
    return JSONResponse(content=doc)

@app.get("/data/list")
async def list_files(token: dict = Depends(verify_token)):
    cursor = collection.find({}, {"filename": 1, "_id": 0})
    files = [doc["filename"] async for doc in cursor]
    return {"files": files}
