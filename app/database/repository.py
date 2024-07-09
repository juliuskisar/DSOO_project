from app.bootstrap import ApplicationBootstrap
from app.database.schema import ClientSchema, ProductSchema

class Repository:
    def __init__(self):
        self.client = ApplicationBootstrap().get_mongo_client().clients
        self.product = ApplicationBootstrap().get_mongo_client().products

    def get_client(self, **kwargs) -> ClientSchema:
        client = self.client.find_one(kwargs)
        client = ClientSchema(**client)
        return client

    async def update_client(self, **kwargs) -> bool:
        filter = {"client_uuid": kwargs["client_uuid"]}
        new_values = {"$set": kwargs}
        self.client.update_one(filter, new_values)
        return True

    async def get_all_clients(self) -> dict:
        clients = self.client.find()
        return [ClientSchema(**client) for client in clients]
    
    async def get_all_products(self) -> dict:
        products = self.product.find()
        return [ProductSchema(**product) for product in products]

    def get_product(self, **kwargs) -> ProductSchema:
        product = self.product.find_one(kwargs)
        product = ProductSchema(**product)
        return product



    async def populate_client(self, data):
        self.client.insert_many(data)
        return True
    
    async def populate_product(self, data):
        self.product.insert_many(data)
        return True
