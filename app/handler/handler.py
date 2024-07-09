from app.database.schema import UpdateCriteria
from app.service.service import Service
from fastapi import APIRouter, UploadFile
from fastapi_utils.cbv import cbv
from uuid import uuid4

router = APIRouter()


@cbv(router)
class Handler:
    def __init__(self):
        self.service = Service()

    @router.get("/client/{client_uuid}")
    def get_client(self, client_uuid: str):
        client = self.service.get_client(client_uuid=client_uuid)
        return client
    

    @router.post("/populate_client")
    async def populate_client(self, number_of_clients: int):
        return await self.service.populate_client(number_of_clients=number_of_clients)
    
    # @router.post("/populate_product")
    # async def populate_product(self):
    #     contents = document.file.read()
    #     contents = contents.decode('utf-8')
    #     return await self.service.populate_product(contents=contents)

    @router.post("/populate_favorites")
    async def populate_favorites(self, update_criteria: UpdateCriteria = None):
        return await self.service.populate_favorites(update_criteria=update_criteria)
    
    @router.post("/purchase_round")
    async def purchase_round(self):
        return await self.service.purchase_round()