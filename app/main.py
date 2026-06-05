from fastapi import FastAPI
from app.database import Base, engine
from app import models  

app = FastAPI(title="Electronic Dean's Office")

@app.get("/")
def root():
    return {"message": "Electronic Dean's Office API"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "SQLite",
        "tables": len(Base.metadata.tables)
    }