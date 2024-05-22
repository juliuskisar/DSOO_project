from time import sleep
import requests
from app.database.repository import Repository
import settings

import json


class Service:
    def __init__(self):
        self.repository = Repository()

    def get_client(self, client_uuid: str):
        client = self.repository.get_example(client_uuid)
        return client
