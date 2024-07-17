from app.database.schema import PurchaseSchema, UpdateCriteria
from app.service.service import Service
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from uuid import uuid4

router = APIRouter()


@cbv(router)
class Effectors:
    def __init__(self):
        self.service = Service()

    @router.post("/update_favorite_model")
    async def update_favorite_model(self, plan: UpdateCriteria = None):
        return await self.service.populate_favorites(plan=plan)
    
    @router.post("/purchase_round")
    async def purchase_round(self):
        return await self.service.purchase_round()
    
    @router.post("/populate_general_data")
    async def populate_general_data(self):
        return await self.service.populate_general_data()
    
    @router.get("/client/{client_uuid}")
    def get_client(self, client_uuid: str):
        client = self.service.get_client(client_uuid=client_uuid)
        return client
    
    @router.post("/populate_client")
    async def populate_client(self, number_of_clients: int):
        return await self.service.populate_client(number_of_clients=number_of_clients)
