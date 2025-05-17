from sqlalchemy.orm import Session
from . import models, schemas

def get_words(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Word).offset(skip).limit(limit).all()

def create_word(db: Session, word: schemas.WordCreate):
    db_word = models.Word(word=word.word, translation=word.translation)
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word
