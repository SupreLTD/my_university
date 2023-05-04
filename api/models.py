import re
import uuid
from fastapi import HTTPException
from pydantic import EmailStr, BaseModel, validator

LETTER_MATCH_PATTERN = re.compile(r"[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        """Convert even non dict obj to json"""
        orm_mode = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr

    @validator('name')
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=422, detail='Имя должно содержать только буквы')
        return value

    @validator('surname')
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=422, detail='Фамилия должно содержать только буквы')
        return value
