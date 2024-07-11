from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from typing import Optional



class CustomBaseModel(BaseModel):
    created_at: datetime | str = datetime.now()
    updated_at: datetime | str = datetime.now()
    deleted_at: Optional[datetime] | str = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
    
    def to_dict(self):
        return self.model_dump()
    
    def stringnify_time(self):
        self.updated_at = self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        if self.deleted_at:
            self.deleted_at = self.deleted_at.strftime("%Y-%m-%d %H:%M:%S")
        return self.model_dump()


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
    total_clients: int | None = None
    average_value_per_client: float | None = None
    average_items_per_client: float | None = None
    diferent_products: int | None = None



class UpdateCriteria(BaseModel):
    total_items: int | None = None
    total_value: float | None = None
    total_clients: int | None = None
    average_value_per_client: float | None = None
    average_items_per_client: float | None = None
    diferent_products: int | None = None


class BreakCondition(CustomBaseModel):
    break_condition: bool = False


class GoalsSchema(BaseModel):
    total_items: int | None = None
    total_value: float | None = None
    total_clients: int | None = None
    average_value_per_client: float | None = None
    average_items_per_client: float | None = None
    diferent_products: int | None = None


class SymptomSchema(BaseModel):
    update_symptom: bool = False
    symptoms: list = []
