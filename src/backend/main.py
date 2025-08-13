from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from database import SessionLocal, engine, Base
from routers import admin, company, supplier, public, auth

# Carica variabili ambiente
load_dotenv()

# Crea tabelle database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Piattaforma NIS2 Supplier Assessment",
    description="Piattaforma per la valutazione della conformità fornitori secondo Direttiva NIS2",
    version="1.0.0"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend Vue.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency per database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Security
security = HTTPBearer()

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(company.router, prefix="/api/company", tags=["company"])
app.include_router(supplier.router, prefix="/api/supplier", tags=["supplier"])
app.include_router(public.router, prefix="/v", tags=["public"])

# Servire file statici per PDF e risorse
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Piattaforma NIS2 Supplier Assessment API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nis2-platform-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 