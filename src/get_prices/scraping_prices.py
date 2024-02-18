import random
from utils import USER_AGENT_LIST, logger
import os
import aiohttp
import asyncio
import json

class PricesEans():

    def __init__(self, category_l1, category_l2) -> None:
        # URL base and headers
        self.url_base = "https://www.byggmakker.no/api/price/stores/product/"
        self.headers = {"User-Agent": random.choice(USER_AGENT_LIST)}
        self.__category_l1 = category_l1
        self.__category_l2 = category_l2
        self.folder_path = os.path.join('data', category_l1, category_l2, 'prices')
        self.create_folders(self.folder_path)

    def create_folders(self, folder_path):
        # Create folder path if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.info(f"Created directory: {self.folder_path}")

    def create_payload(self):
        self.directory = f'data/{self.__category_l1}/{self.__category_l2}/availability'
        self.create_folders(self.directory)

        # List all files in the directory
        files = os.listdir(self.directory)

        data_payload = []
        # Iterate over each file
        for filename in files:
            filepath = os.path.join(self.directory, filename)
            with open(filepath, 'r') as json_file:
                products = json.load(json_file)
                
            stores_list = []
            for store in products['storeAvailabilities']:
                stores_list.append(store['store']['id'])

            data_payload.append({
                'ean': products['ean'],
                'storeIds': stores_list
            })

        self.payload_filepath = f'{self.folder_path}/data_payload/'
        self.create_folders(self.payload_filepath)

        with open(self.payload_filepath + 'data_payload.json', 'w') as json_file:
            json.dump(data_payload, json_file, indent=4)
    
    async def fetch_product(self, session, data):
        async with session.post(self.url_base, headers=self.headers, json=data) as response:
            try:
                json_response = await response.json()
                # Save all_products to a JSON file
                with open(os.path.join(self.folder_path, f"{data['ean']}_prices.json"), 'w') as json_file:
                    json.dump(json_response, json_file)
            except json.JSONDecodeError as e:
                logger.error(f"Error getting prices for {data['ean']}: {e}")
    
    async def scraping_prices(self):
        logger.info(f"Scraping prices for {self.__category_l1}/{self.__category_l2} started.")
        print(f"Scraping prices for {self.__category_l1}/{self.__category_l2} started.")
        self.create_payload()
        async with aiohttp.ClientSession() as session:
            # Reading products id JSON file
            with open(f'{self.folder_path}/data_payload/data_payload.json', 'r') as json_file:
                data_payload = json.load(json_file)
            tasks = [self.fetch_product(session, data) for data in data_payload]
            await asyncio.gather(*tasks)
        logger.info(f"Scraping prices for {self.__category_l1}/{self.__category_l2} finished.")
        print(f"Scraping prices for {self.__category_l1}/{self.__category_l2} finished.")