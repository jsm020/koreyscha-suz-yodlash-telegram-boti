

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database
from .admin import admin



app = FastAPI()
app.mount("/admin", admin)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Backend ishlayapti!"}


# So'zlar ro'yxatini olish
@app.get("/words/", response_model=list[schemas.WordOut])
def read_words(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    words = crud.get_words(db, skip=skip, limit=limit)
    return words

# Yangi so'z qo'shish
@app.post("/words/", response_model=schemas.WordOut)
def create_word(word: schemas.WordCreate, db: Session = Depends(get_db)):
    return crud.create_word(db=db, word=word)
