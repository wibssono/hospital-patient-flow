from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import AfterValidator, BaseModel

app = FastAPI()

def valid_item_id(item_id: str | None) -> (str | None):
    if not item_id:
        return
    if item_id.startswith(("id-", "us-")):
        return item_id
    else:
        error = "Invalid Item"
        raise ValueError (error)

class item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/items/")
# This is a deprecated Query
async def read_items(q: Annotated[str | None, Query(title="Query asked",
                                                    max_length=10, 
                                                    min_length=10,
                                                    deprecated=True)] = None) -> dict[str, str | None]:
    return {"Did you ask": q}

@app.get('/itemvalues/{item_id}/')
async def get_items(q: Annotated[str | None, Query(title="Giving Item", alias="item-give", description="To give back what was taken"))] = None:
