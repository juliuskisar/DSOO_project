
from loguru import logger
from app.database.repository import Repository
from faker import Faker
import random
from datetime import datetime

from app.database.schema import BreakCondition, ClientSchema, PurchaseSchema, SymptomSchema, UpdateCriteria


class Service:
    def __init__(self):
        self.repository = Repository()
    
    async def populate_favorites(self, plan: UpdateCriteria = None):
        clients = await self.repository.get_all_clients()
        products = await self.repository.get_all_products()
        number_of_changes = 0
        for client in clients:
            must_update = await self._check_update_necessity(client, plan)
            if must_update:
                client.favorites_list = random.choices(products, k=5)
                await self.repository.update_client(**client.dict())
                number_of_changes += 1
        logger.info(f"{number_of_changes} clients updated.")
        return {"number of changes": number_of_changes}
    
    async def _check_update_necessity(self, client: ClientSchema, update_criteria: UpdateCriteria):
        if update_criteria.average_value_per_client and client.last_purchase.total_value < update_criteria.average_value_per_client:
            return True
        if update_criteria.average_items_per_client and client.last_purchase.total_items < update_criteria.average_items_per_client:
            return True
        if update_criteria.total_clients and update_criteria.total_clients == 1001:
            return True
        return False
    
    async def purchase_round(self):
        clients = await self.repository.get_all_clients()
        final_value = 0
        final_items = 0
        diferent_products = set()
        for client in clients:
            total_items = 0
            total_value = 0
            for item in client.favorites_list:
                if len(item.name) == client.classification:
                    total_items += 1
                    total_value += item.price
                    diferent_products.add(item.name)
            final_value += total_value
            final_items += total_items
            client.last_purchase = PurchaseSchema(total_items=total_items, total_value=total_value)
            await self.repository.update_client(**client.dict())
        purchase = PurchaseSchema(
            total_value=final_value,
            total_items=final_items,
            total_clients=len(clients),
            average_value_per_client=final_value/len(clients),
            average_items_per_client=final_items/len(clients),
            diferent_products=len(diferent_products),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await self.repository.insert_purchase_monitor(purchase=purchase)
        logger.info(f'purchase round finished. Total value: {final_value:.2f}, Total items: {final_items}, Total clients: {len(clients)}')
        logger.info(f'Average value per client: {final_value/len(clients):.2f}, Average items per client: {final_items/len(clients)}')

        return purchase
    
    async def populate_general_data(self):
        last_purchase = PurchaseSchema(
            total_items=10,
            total_value=1000,
            total_clients=100,
            average_value_per_client=10,
            average_items_per_client=0.10,
            diferent_products=0,
        )
        await self.repository.insert_purchase_monitor(last_purchase)

    async def check_break_condition(self) -> BreakCondition:
            return await self.repository.get_break_condition()

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

    def get_client(self, client_uuid: str):
        client = self.repository.get_client(client_uuid=client_uuid)
        return client
    
    async def populate_client(self, number_of_clients: int):
        fake = Faker()
        clients_to_insert = []
        for _ in range(number_of_clients):
            client_uuid = fake.uuid4()
            name = fake.name()
            email = fake.email()
            gender = random.choice(['Male', 'Female', 'Other'])
            civil_status = random.choice(['Single', 'Married', 'Divorced', 'Widowed'])
            number_of_dependents = random.randint(0, 5)
            education_level = random.choice(['High School', 'Bachelor', 'Master', 'Doctorate'])
            profession = fake.job()
            income = round(random.uniform(20000, 120000), 2)
            number_of_vehicle = random.randint(0, 3)
            number_of_properties = random.randint(0, 3)
            payment_method = random.choice(['Credit Card', 'Debit Card', 'Cash', 'Online Payment'])
            favorite_product = fake.word()
            hobbies = ', '.join(fake.words(nb=3))
            favorite_music_genre = random.choice(['Rock', 'Pop', 'Jazz', 'Classical', 'Electronic', 'Hip-Hop'])
            favorite_brand = fake.company()
            favorite_social_media = random.choice(['Facebook', 'Twitter', 'Instagram', 'LinkedIn', 'TikTok'])
            gadget_used = random.choice(['Smartphone', 'Tablet', 'PC', 'Laptop'])
            classification = random.randint(0, 9)
            
            client = {
                "client_uuid": client_uuid,
                "name": name,
                "email": email,
                "gender": gender,
                "civil_status": civil_status,
                "number_of_dependents": number_of_dependents,
                "education_level": education_level,
                "profession": profession,
                "income": income,
                "number_of_vehicle": number_of_vehicle,
                "number_of_properties": number_of_properties,
                "payment_method": payment_method,
                "favorite_product": favorite_product,
                "last_purchase": None,
                "favorites_list": None,
                "hobbies": hobbies,
                "favorite_music_genre": favorite_music_genre,
                "favorite_brand": favorite_brand,
                "favorite_social_media": favorite_social_media,
                "gadget_used": gadget_used,
                "classification": classification
            }
            clients_to_insert.append(client)
        await self.repository.populate_client(clients_to_insert)
        return {"message": f"{number_of_clients} clients inserted."}
