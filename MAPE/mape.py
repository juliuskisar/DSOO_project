from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter
from app.bootstrap import ApplicationBootstrap
from app.database.schema import BreakCondition, ClientSchema, GoalsSchema, ProductSchema, PurchaseSchema, SymptomSchema, UpdateCriteria
from app.handler.handler import Effectors
from loguru import logger
from time import sleep
from fastapi_utils.cbv import cbv


mape_router = APIRouter()


@cbv(mape_router)
class ControlLoop:
    def __init__(self):
        self.planner = Planner()
        self.analyzer = Analyzer()
        self.monitor = Monitor()
        self.executor = Executor()
    
    @mape_router.get("/start")
    async def run(self):
        logger.info("Control Loop has been started.")
        number_of_loops = 0
        await self.monitor.start_event_loop()
        while True:
            sleep(2)
            event: bool = await self.monitor.store_event()
            symptom: SymptomSchema = await self.analyzer.analyze(event)
            plan = await self.planner.plan(symptom)
            await self.executor.execute(plan)
            must_break = await self.monitor.check_break_condition()
            number_of_loops += 1
            logger.info(f"Control Loop has been running for {number_of_loops} loops.")
            if must_break:
                logger.info("Control Loop has been stopped.")
                break


class Planner:
    def __init__(self):
        self.executor = Executor()
        self.repository = KnowledgeBase()
    
    async def plan(self, symptom: SymptomSchema = None) -> UpdateCriteria:
        goals = await self.repository.get_goals()
        if symptom is None or not symptom.update_symptom:
            logger.info('nothing to plan')
            logger.info('no symptoms detected, improving goals')
            logger.info('updating goals in 5%')
            for field in goals.model_fields:
                goals_value = getattr(goals, field)
                updated_goals_value = round(goals_value * 1.05) if isinstance(goals_value, int) else goals_value * 1.05
                setattr(goals, field, updated_goals_value)
                await self.repository.update_goals(goals)
            return None
        update_criteria = dict()
        for field in symptom.symptoms:
            goals_value = getattr(goals, field)
            update_criteria[field] = goals_value
        print('analysing_', end='')
        sleep(1)
        print('_'*50, end='')
        print('_'*100)
        logger.info(f'must update fields: {update_criteria}')
        return UpdateCriteria(**update_criteria)


class Analyzer:
    def __init__(self):
        self.symptom = Symptom()
        self.repository = KnowledgeBase()

    async def analyze(self, event: bool) -> SymptomSchema:
        if not event:
            logger.info('nothing to analyse')
            return None
        logger.info('analysing')
        return await self.symptom.get_symptom()
        

class Symptom:
    def __init__(self):
        self.repository = KnowledgeBase()

    async def get_symptom(self) -> SymptomSchema:
        return await self.repository.get_symptom()


class Monitor:
    def __init__(self):
        self.sensors = Sensors()

    async def start_event_loop(self) -> None:
        await self.sensors.cancel_break_condition()

    async def check_break_condition(self) -> bool:
        condition = await self.sensors.check_break_condition()
        return condition.break_condition

    async def store_event(self) -> PurchaseSchema:
        return await self.sensors.store_event()


class Sensors:
    def __init__(self):
        self.repository = KnowledgeBase()

    async def check_break_condition(self) -> BreakCondition:
        return await self.repository.get_break_condition()

    async def cancel_break_condition(self) -> None:
        await self.repository.cancel_break_condition()

    async def store_event(self) -> PurchaseSchema:
        last_purchase = await self.repository.get_last_purchase()
        goals = await self.repository.get_goals()
        # resetando sintomas
        symptom_schema = SymptomSchema(update_symptom=False, symptoms=[])
        await self.repository.update_symptom(symptom_schema)
        has_to_update_symptom, symptom = await self._check_goals(last_purchase, goals)
        if has_to_update_symptom:
            logger.info(f'problems are detected: {symptom}')
            symptom_schema = SymptomSchema(update_symptom=True, symptoms=symptom)
            await self.repository.update_symptom(symptom_schema)
            return True

        return False

    async def _check_goals(self, last_purchase, goals) -> bool:
        count_greater = 0
        greater_items = []

        for field in goals.__fields__:
            goals_value = getattr(goals, field)
            purchase_value = getattr(last_purchase, field)
            if goals_value is not None and purchase_value is not None and goals_value > purchase_value:
                count_greater += 1
                greater_items.append(field)

            if count_greater >= 2:
                return True, greater_items
        
        return False, greater_items


class Executor:
    def __init__(self):
        self.effectors = Effectors()

    async def execute(self, plan = None):
        if plan:
            await self.effectors.update_favorite_model(plan)
        await self.effectors.purchase_round()


class KnowledgeBase:
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
    
    async def update_goals(self, goals: GoalsSchema):
        self.goals.update_one({}, {"$set": goals.model_dump()})
        return True

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
