from datetime import datetime
from app.bootstrap import ApplicationBootstrap
from app.database.schema import BreakCondition, ClientSchema, GoalsSchema, ProductSchema, PurchaseSchema, SymptomSchema

class Repository:
    def __init__(self):
        self.client = ApplicationBootstrap().get_mongo_client().clients
        self.product = ApplicationBootstrap().get_mongo_client().products
        self.monitor = ApplicationBootstrap().get_mongo_client().monitor
        self.purchase_monitor = ApplicationBootstrap().get_mongo_client().purchase_monitor
        self.symptom = ApplicationBootstrap().get_mongo_client().symptom
        self.goals = ApplicationBootstrap().get_mongo_client().goals

    def get_client(self, **kwargs) -> ClientSchema:
        client = self.client.find_one(kwargs)
        client = ClientSchema(**client)
        return client

    async def update_client(self, **kwargs) -> bool:
        filter = {"client_uuid": kwargs["client_uuid"]}
        new_values = {"$set": kwargs}
        self.client.update_one(filter, new_values)
        return True

    async def get_all_clients(self) -> list[ClientSchema]:
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
    
    async def get_break_condition(self):
        break_condition = self.monitor.find_one()
        return BreakCondition(**break_condition)
    
    async def cancel_break_condition(self):
        self.monitor.update_one({}, {"$set": {"break_condition": False, "updated_at": datetime.now()}})
        return True

    async def get_last_purchase(self):
        purchase = self.purchase_monitor.find()
        last_purchase = next(purchase.sort("updated_at", -1).limit(1))
        return PurchaseSchema(**last_purchase)

    async def insert_symptom(self, symptom: SymptomSchema):
        self.symptom.insert_one(symptom.model_dump())
        return True
    
    async def insert_break_condition(self, break_state: BreakCondition):
        self.monitor.insert_one(break_state.to_dict())
        return True
    
    async def get_goals(self) -> GoalsSchema:
        goals = self.goals.find_one()
        return GoalsSchema(**goals)
    
    async def update_symptom(self, symptom: SymptomSchema):
        self.symptom.update_one({}, {"$set": {"update_symptom": symptom.update_symptom, "symptoms": symptom.symptoms}})
    
    async def get_symptom(self) -> SymptomSchema:
        symptom = self.symptom.find_one()
        return SymptomSchema(**symptom)
    
    async def insert_purchase_monitor(self, purchase: PurchaseSchema):
        self.purchase_monitor.insert_one(purchase.model_dump())
        return True
