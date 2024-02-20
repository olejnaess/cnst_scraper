import json
from pymongo import MongoClient
from datetime import datetime


def update_product_descriptions():
    client = MongoClient(
        'mongodb+srv://svenn:4eNBZS0ildGeb5fe@svennproducts.33s9rtm.mongodb.net/')
    db = client.svenn_products_db
    products_collection = db.products

    # Load the aggregated product descriptions
    with open('data\gulv\laminatgulv\product_description.json', 'r') as file:
        product_descriptions = json.load(file)

    for product in product_descriptions:
        ean = product.get('ean')
        if ean:
            # Prepare the document update with the required fields
            update_document = {
                "$set": {
                    # Update the base_name with the name from the product description
                    "base_name": product.get("name", ""),
                    # Update the brandName
                    "brandName": product.get("brandName", ""),
                    # Extract unit from measurements
                    "unit": product.get("measurements", {}).get("netContent", {}).get("unit", ""),
                    # Update the images array
                    "images": product.get("images", []),
                }
            }
            update_result = products_collection.update_one(
                {"ean_codes": ean},
                update_document,
                upsert=False  # Only update existing documents, do not insert new ones
            )

            if update_result.modified_count > 0:
                print(f"Updated document with EAN: {ean}")
            else:
                print(
                    f"No changes made for EAN: {ean}, document may not exist.")

    client.close()


if __name__ == '__main__':
    update_product_descriptions()
