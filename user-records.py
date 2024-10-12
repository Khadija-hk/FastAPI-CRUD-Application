from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

app = FastAPI()

# MongoDB connection string
MONGODB_URL = "mongodb+srv://admin:7mltZPOuUYebLOeh@cluster0.hqwor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.get_database("mydatabase")

# Clock-In Record Model
class ClockInRecord(BaseModel):
    id: int
    email: str
    location: str
    insert_date: datetime  # Automatically set during clock-in

# Pydantic model for updating Clock-In Records
class UpdateClockInRecord(BaseModel):
    email: Optional[str]  # Made optional for updates
    location: Optional[str]  # Made optional for updates

# Root message to check if the API is working 
@app.get("/")
def read_root():
    return {"message": "success"}

# API to create a new clock-in entry
@app.post("/clock-in/", response_model=ClockInRecord)
async def create_clock_in(clock_in: ClockInRecord):
    clock_in_dict = clock_in.dict()
    clock_in_dict["insert_date"] = datetime.now()  # Set insert date to now
    clock_in_dict["_id"] = clock_in_dict.pop("id")  # Use user-provided id as _id in MongoDB
    
    await db.clock_in.insert_one(clock_in_dict)
    # Return the response with the correct id field
    return ClockInRecord(**{**clock_in_dict, "id": clock_in_dict["_id"]})

# API to retrieve a clock-in record by ID
@app.get("/clock-in/{record_id}", response_model=ClockInRecord)
async def read_clock_in(record_id: int):
    clock_in_record = await db.clock_in.find_one({"_id": record_id})  # Using user-provided ID as _id
    if clock_in_record is None:
        raise HTTPException(status_code=404, detail="Clock-in record not found")
    # Return the response with the correct id field
    return ClockInRecord(**{**clock_in_record, "id": clock_in_record["_id"]})

# API to filter clock-in records
@app.get("/clock-in/filter", response_model=List[ClockInRecord])
async def filter_clock_ins(
    email: Optional[str] = None,
    location: Optional[str] = None,
    after: Optional[datetime] = None
):
    query = {}
    
    if email:
        query['email'] = email
    if location:
        query['location'] = location
    if after:
        query['insert_date'] = {"$gt": after}

    # Fetch clock-in records based on the query
    clock_in_records = await db.clock_in.find(query).to_list(100)
    
    if not clock_in_records:
        raise HTTPException(status_code=404, detail="No clock-in records found matching the criteria.")

    # Return clock-in records with id field instead of _id
    return [ClockInRecord(**{**record, "id": record["_id"]}) for record in clock_in_records]

# API to delete a clock-in record
@app.delete("/clock-in/{record_id}")
async def delete_clock_in(record_id: int):
    deleted = await db.clock_in.delete_one({"_id": record_id})  # Using normal ID
    if deleted.deleted_count == 1:
        return {"message": "Clock-in record deleted successfully"}
    raise HTTPException(status_code=404, detail="Clock-in record not found")

@app.put("/clock-in/{record_id}", response_model=ClockInRecord)
async def update_clock_in(record_id: int, updated_clock_in: UpdateClockInRecord):
    update_data = {}

    if updated_clock_in.email is not None:  # Allow email to be updated if provided
        update_data["email"] = updated_clock_in.email
    if updated_clock_in.location is not None:  # Allow location to be updated if provided
        update_data["location"] = updated_clock_in.location

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Update the record in the database
    updated = await db.clock_in.update_one(
        {"_id": record_id},
        {"$set": update_data}
    )

    if updated.modified_count == 1:
        # Fetch the updated record
        clock_in_record = await db.clock_in.find_one({"_id": record_id})

        # Map the fields manually to match the response model
        return ClockInRecord(
            id=clock_in_record["_id"],  # Use the database's _id as the id
            email=clock_in_record["email"],
            location=clock_in_record["location"],
            insert_date=clock_in_record["insert_date"]
        )

    raise HTTPException(status_code=404, detail="Clock-in record not found")
