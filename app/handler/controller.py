from app.service.service import Service
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from uuid import uuid4

router = APIRouter()


@cbv(router)
class Controller:
    def __init__(self):
        self.service = Service()

    @router.get("/client/{client_uuid}")
    def get_client(self, client_uuid: str):
        client_uuid = f'client_{str(uuid4())}'
        client = self.service.get_client(client_uuid=client_uuid)
        return client
