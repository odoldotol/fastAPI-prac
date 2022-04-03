from enum import Enum # 경로 나열 아래 보기

from fastapi import FastAPI, Path, Query
from pydantic import BaseModel # 타입 정의하는데 도움

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., title="The ID of the item to get"),
    q: str | None = Query(None, min_length=3, max_length=50, regex="^fixedquery$"), # 정규표현식
    p: str = Query(..., min_length=3), # 필수
    r: list[str] | None = Query(None), # 쿼리로 쓰러면 이렇게 명시적으로 선언해줘야 바디로 해석되는거 막음
    skip: int = 0, limit: int = 10, short: bool = False
    ):
    item = {"item_id": item_id, "fakeitemdb": fake_items_db[skip : skip + limit]}
    if q:
        item.update({"q": q})
    if p:
        item.update({"p": p})
    if r:
        item.update({"r": r})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.post("/items/")
async def create_item(item: Item):
    # item.name + item.price
    return item


@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet": # ModelName.lenet.value
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}