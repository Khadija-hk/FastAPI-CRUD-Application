from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import date, datetime
from typing import Optional, List
from dateutil.parser import parse  # For parsing dates from strings
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO)


app = FastAPI()

# MongoDB connection string
MONGODB_URL = "mongodb+srv://admin:7mltZPOuUYebLOeh@cluster0.hqwor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.get_database("mydatabase")

class Item(BaseModel):
    id: str
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: date
    insert_date : Optional[date] = None


@app.get("/")
def read_root():
    return {"message": "success"}


@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item_dict = item.model_dump()  # Use .model_dump() instead of .dict()
    item_dict['expiry_date'] = item.expiry_date.isoformat()  # Convert date to string (ISO format) for MongoDB
    item_dict['insert_date'] = datetime.now().date().isoformat()   # Use UTC for consistency
    item_dict["_id"] = item.id 
    await db.items.insert_one(item_dict)
    return {**item_dict, "_id": item_dict["_id"]}


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    # Find the item by custom ID
    item = await db.items.find_one({"_id": item_id})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

'''@app.get("/items/filter", response_model=List[Item])
async def filter_items(
    email: Optional[str] = None,
    expiry_date: Optional[date] = None,
    insert_date: Optional[date] = None,
    quantity: Optional[int] = None
):
    # Use logging to debug
    logging.info("Filter endpoint hit")

    # Initialize an empty query dictionary
    query = {}

    # Add email filter
    if email:
        query['email'] = email  # Exact match for email

    # Add expiry date filter
    if expiry_date:
        query['expiry_date'] = {"$gt": expiry_date}

    # Add insert date filter
    if insert_date:
        query['insert_date'] = {"$gt": insert_date}

    # Add quantity filter
    if quantity is not None:
        query['quantity'] = {"$gte": quantity}

    # Debugging: Print the constructed query to verify
    print(f"Constructed query: {query}")

    # Execute the query and fetch the items
    items = await db.items.find(query).to_list(100)

    # If no items match the query, raise a 404 error
    if not items:
        raise HTTPException(status_code=404, detail="No items found matching the criteria.")
    
    return items'''

@app.get("/items/filter")
async def filter_items():
    logging.info("Filter endpoint reached")
    return {"message": "Filter endpoint works"}



@app.get("/items/", response_model=List[Item])
async def list_items():
    items = await db.items.find().to_list(100)  # Retrieves up to 100 items
    return items

@app.get("/items/filter/email", response_model=List[Item])
async def filter_by_email(email: str):
    query = {"email": email}
    items = await db.items.find(query).to_list(100)
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    return items


'''
# Update an Item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, updated_item: Item):
    updated = await items_collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": updated_item.dict()}
    )
    if updated.modified_count == 1:
        return await items_collection.find_one({"_id": ObjectId(item_id)})
    raise HTTPException(status_code=404, detail="Item not found")

# Delete an Item
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    deleted = await items_collection.delete_one({"_id": ObjectId(item_id)})
    if deleted.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")'''
