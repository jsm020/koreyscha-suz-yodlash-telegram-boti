from pydantic import BaseModel

class WordBase(BaseModel):
    word: str
    translation: str

class WordCreate(WordBase):
    pass

class WordOut(WordBase):
    id: int
    class Config:
        orm_mode = True
