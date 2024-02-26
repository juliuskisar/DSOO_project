from app.bootstrap import ApplicationBootstrap
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class CustomBaseModel(BaseModel):
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ExampleSchema(CustomBaseModel):
    uuid: str
    name: str


class ClientSchema(CustomBaseModel):
    client_uuid: str
    email: str
    password: str


class PictoreSchema(CustomBaseModel):
    picture_uuid: str
    client_uuid: str
    name: str
    file_name: str
    is_healty: bool
    ingredients: dict
    total_calories: str
    nutrients: dict
    picture_base_64: str

    
