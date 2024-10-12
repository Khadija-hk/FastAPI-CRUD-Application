# FastAPI CRUD Application with MongoDB

A FastAPI application that provides CRUD (Create, Read, Update, Delete) functionality for managing items and clock-in records, utilizing MongoDB for data storage.

## Key Features

- **Item Management:** Create, retrieve, update, and delete items.
- **Filtering:** Filter items by email or expiration date.
- **Aggregation:** Aggregate items by email for data insights.
- **Clock-In Records:** Create and manage user clock-in records.
- **Async MongoDB Operations:** Powered by FastAPI and Motor for asynchronous database interactions.

## Prerequisites

- **Python 3.7+**: Ensure Python is installed on your system.
- **MongoDB**: Set up a local or cloud MongoDB instance.
- **Required Python Packages**: Install dependencies listed below.

## Installation

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/Khadija-hk/your-repo-name.git
cd your-repo-name
```

### Step 2: Install Dependencies

Use `pip` to install the necessary Python packages:

```bash
pip install fastapi[all] motor python-dateutil
```

### Step 3: Configure MongoDB

Update the MongoDB connection string in your application code (usually in `main.py`) with your MongoDB instance details.

## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

This will run the application locally, accessible at `http://127.0.0.1:8000`.

## API Endpoints

### Item Endpoints

- **Create Item**:  
  `POST /items/`  
  Add a new item to the database.
  
- **Retrieve Item by ID**:  
  `GET /items/{item_id}`  
  Get details of a specific item by its ID.
  
- **Update Item by ID**:  
  `PUT /items/{item_id}`  
  Update the details of an existing item.
  
- **Delete Item by ID**:  
  `DELETE /items/{item_id}`  
  Remove an item from the database.
  
- **Filter Items by Email**:  
  `GET /items/filter/email`  
  Retrieve items based on the provided email.
  
- **Aggregate Items by Email**:  
  `GET /items/aggregate`  
  Aggregate items grouped by email.

### Clock-In Endpoints

- **Create Clock-In Record**:  
  `POST /clock-in/`  
  Record a new clock-in event for a user.
  
- **Retrieve Clock-In Record by ID**:  
  `GET /clock-in/{record_id}`  
  Get details of a specific clock-in record by its ID.
  
- **Delete Clock-In Record by ID**:  
  `DELETE /clock-in/{record_id}`  
  Remove a clock-in record from the database.
  
- **Filter Clock-In Records**:  
  `GET /clock-in/filter`  
  Retrieve clock-in records based on user-defined filters.

---

Feel free to customize this as per your project’s requirements!

