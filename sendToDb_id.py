import json
from pymongo import MongoClient
from datetime import datetime

client = MongoClient(
    'mongodb+srv://svenn:4eNBZS0ildGeb5fe@svennproducts.33s9rtm.mongodb.net/')
db = client.svenn_products_db
products_collection = db.products

# Load product IDs and links from JSON file
with open('data/gulv/laminatgulv/products_ids.json', 'r') as file:
    products_data = json.load(file)

with open('data/gulv/laminatgulv/products_description.json', 'r') as file:
    products_description = json.load(file)

for product in products_data:
    # Prepare the update document
    update_document = {
        "$set": {
            "last_updated": datetime.utcnow(),  # Update the last_updated field
            "variants": [
                {
                    "retailer": "Byggmakker",
                    "url_product": product['link'],
                    "ean_codes": [product['id']],
                }
            ]
        },
        "$setOnInsert": {
            "created": datetime.utcnow(),  # Set the created field only on insert
            "ean_codes": [product['id']],  # Include on insert
        }
    }

    # Perform the upsert operation
    result = products_collection.update_one(
        # Query for the document with matching ean_codes
        {"ean_codes": [product['id']]},
        update_document,
        upsert=True  # Create a new document if one doesn't exist
    )

    if result.upserted_id:
        print(f"Inserted new document with ID: {result.upserted_id}")
    else:
        print(f"Updated document with product ID: {product['id']}")

# Optionally, close the client connection
client.close()
