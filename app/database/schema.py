from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from typing import Optional



class CustomBaseModel(BaseModel):
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
    
    @classmethod
    def to_dict(cls, obj):
        return obj.dict()


class ClientSchema(BaseModel):
    # dados pessoais
    client_uuid: str
    name: str
    email: str
    gender: str
    civil_status: str
    number_of_dependents: int
    # dados socioeconomicos
    education_level: str
    profession: str
    income: float
    number_of_vehicle: int
    number_of_properties: int
    # dados de compra
    payment_method: str
    favorite_product: str
    last_purchase: PurchaseSchema | None
    favorites_list: list[ProductSchema] | None
    # dados de hábitos
    hobbies: str
    favorite_music_genre: str
    favorite_brand: str
    favorite_social_media: str
    # dados técnicos
    gadget_used: str
    # critério de classificação
    classification: int # um número de 0 a 9



class ProductSchema(BaseModel):
    product_uuid: str
    name: str
    price: float
    category: str
    brand: str
    provider: str
    description: str


class PurchaseSchema(CustomBaseModel):
    total_items: int | None = None
    total_value: float | None = None


class UpdateCriteria(BaseModel):
    value: float | None = None
    total_items: int | None = None
    new_items: bool | None = None
