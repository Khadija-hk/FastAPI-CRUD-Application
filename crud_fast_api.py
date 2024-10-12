from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import date, datetime
from typing import Optional, List
from dateutil.parser import parse  # For parsing dates from strings

# Declare the FastAPI
app = FastAPI()

# MongoDB connection string
MONGODB_URL = "mongodb+srv://admin:7mltZPOuUYebLOeh@cluster0.hqwor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.get_database("mydatabase")

# Pydrantic model
class Item(BaseModel):
    id: str
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: date

class EmailCount(BaseModel):
    email: str
    item_count: int

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    expiry_date: Optional[date] = None


# Root message to check if the API is working 
@app.get("/")
def read_root():
    return {"message": "success"}

# API to add items to the Database
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item_dict = item.model_dump()  # Use .model_dump() instead of .dict()
    item_dict['expiry_date'] = item.expiry_date.isoformat()  # Convert date to string (ISO format) for MongoDB
    item_dict['insert_date'] = datetime.now().date().isoformat()   # Use UTC for consistency
    item_dict["_id"] = item.id 
    await db.items.insert_one(item_dict)
    return {**item_dict, "_id": item_dict["_id"]}

# API to retrieve an item based on the ID
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    # Find the item by custom ID
    item = await db.items.find_one({"_id": item_id})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# API to filter the items based on the email 
@app.get("/items/filter/email", response_model=List[Item])
async def filter_by_email(email: str):
    query = {"email": email}
    items = await db.items.find(query).to_list(100)
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    return items

@app.get("/items/aggregate", response_model=List[EmailCount])
async def aggregate_items():
    pipeline = [
        {
            "$group": {
                "_id": "$email",
                "item_count": {"$sum": 1}
            }
        }
    ]
    
    result = await db.items.aggregate(pipeline).to_list(length=None)
    
    aggregated_results = [
        EmailCount(email=item["_id"], item_count=item["item_count"]) for item in result
    ]
    
    if not aggregated_results:
        return {"message": "No items found."}
    
    return aggregated_results

# Update an Item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, updated_item: ItemUpdate):
    update_data = {}

    if updated_item.name is not None:
        update_data["name"] = updated_item.name
    if updated_item.email is not None:
        update_data["email"] = updated_item.email
    if updated_item.item_name is not None:
        update_data["item_name"] = updated_item.item_name
    if updated_item.quantity is not None:
        update_data["quantity"] = updated_item.quantity
    if updated_item.expiry_date is not None:
        update_data["expiry_date"] = updated_item.expiry_date.isoformat()

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await db.items.update_one(
        {"_id": item_id},
        {"$set": update_data}
    )

    if updated.modified_count == 1:
        item = await db.items.find_one({"_id": item_id})
        return item
    raise HTTPException(status_code=404, detail="Item not found")


# Delete an Item
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    deleted = await db.items.delete_one({"_id": item_id})  # Use the integer item_id directly
    if deleted.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# API to filter the items based on optional criteria
@app.get("/items/filter", response_model=List[Item])
async def filter_items(
    email: Optional[str] = None,
    expiry_date: Optional[date] = None,
    insert_date: Optional[date] = None,
    quantity: Optional[int] = None
):

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
    
    return items
