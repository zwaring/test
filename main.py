from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path

app = FastAPI(title="JSON Data API")

# Data model
class Item(BaseModel):
    id: int
    name: str
    description: str
    category: str
    price: float

# Load data from JSON file
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"items": []}

# Save data to JSON file
def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

@app.get("/")
async def root():
    return {"message": "Welcome to the JSON Data API"}

@app.get("/items", response_model=List[Item])
async def get_items():
    data = load_data()
    return data["items"]

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    data = load_data()
    item = next((item for item in data["items"] if item["id"] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/items/category/{category}", response_model=List[Item])
async def get_items_by_category(category: str):
    data = load_data()
    items = [item for item in data["items"] if item["category"] == category]
    return items

@app.get("/items/search/")
async def search_items(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None
):
    data = load_data()
    items = data["items"]
    
    if min_price is not None:
        items = [item for item in items if item["price"] >= min_price]
    if max_price is not None:
        items = [item for item in items if item["price"] <= max_price]
    if category is not None:
        items = [item for item in items if item["category"] == category]
        
    return items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 