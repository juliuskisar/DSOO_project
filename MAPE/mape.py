from fastapi import APIRouter
from app.database.repository import Repository
from app.database.schema import BreakCondition, PurchaseSchema, SymptomSchema, UpdateCriteria
from app.handler.handler import Handler
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
        self.repository = Repository()
    
    async def plan(self, symptom: SymptomSchema = None) -> UpdateCriteria:
        if symptom is None or not symptom.update_symptom:
            logger.info('nothing to plan')
            return None
        goals = await self.repository.get_goals()
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
        self.repository = Repository()

    async def analyze(self, event: bool) -> SymptomSchema:
        if not event:
            logger.info('nothing to analyse')
            return None
        logger.info('analysing')
        return await self.symptom.get_symptom()
        
            

class Symptom:
    def __init__(self):
        self.repository = Repository()

    async def get_symptom(self) -> SymptomSchema:
        return await self.repository.get_symptom()


class Monitor:
    def __init__(self):
        self.event = Event()

    async def start_event_loop(self) -> None:
        await self.event.cancel_break_condition()

    async def check_break_condition(self) -> bool:
        condition = await self.event.check_break_condition()
        return condition.break_condition

    async def store_event(self) -> PurchaseSchema:
        return await self.event.store_event()



class Event:
    def __init__(self):
        self.repository = Repository()

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
        self.handler = Handler()

    async def execute(self, plan = None):
        if plan:
            await self.handler.update_favorite_model(plan)
        await self.handler.purchase_round()


class KnowledgeBase:
    def __init__(self):
        self.repository = Repository()
