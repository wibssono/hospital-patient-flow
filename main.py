from fastapi import FastAPI
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

# Basics of FASTAPI
@app.get('/')
async def root() -> dict[str, str]:
    return {"message": "Hello world!"}

# Path Parameters
@app.get('/items/{item_id}')
async def read_item(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}

## Order Matters
@app.get('/users/me')
async def read_user_me() -> dict[str, str]:
    return {"user_id": "This is current user"}

@app.get('/users/{user_id}')
async def read_user(user_id: str) -> dict[str, str]:
    return {"user_id": user_id}

## Predefined Values
@app.get('/models/{model_name}')
async def read_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Let's go ALEX!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "BOOYAH lenet! You're a machine!"}
    return {"model_name": model_name, "message": f"You're doing okay {model_name.value}"}

## Path Converter
@app.get('/files/{path:path}')
async def get_path(path: str) -> dict[str, str]:
    return {"path": path} 

# Query Parameters
## Defaults
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get('/items_list/')
async def read_query(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

## Optional Parameters & type conversion
@app.get('/queries/{query_id}')
async def get_query(query_id: str, q: str | None = None, short: bool = False) -> dict[str, str]:
    queries = {"queries": query_id}
    if q:
        queries.update({"question": q}) 
    if short:
        queries.update({"short": "Admin"})
    return queries
