from enum import Enum # 경로 나열 아래 보기

from fastapi import FastAPI, Path, Query, Body, Cookie, Header, status, Form, HTTPException, Depends
from pydantic import BaseModel, Field, HttpUrl, EmailStr

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl = Field(None, example="https://example.com/image.png")
    name: str


class Item(BaseModel):
    name: str
    description: str | None = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = set()
    image: list[Image] | None = None

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "Foo",
    #             "description": "A very nice Item",
    #             "price": 35.4,
    #             "tax": 3.2,
    #         }
    #     }

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class User(BaseModel):
    username: str
    full_name: str | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]




fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]



class Tags(Enum):
    items = "items"
    users = "users"




@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/", tags=[Tags.items])
async def read_items(ads_id: str | None = Cookie(None), user_agent: str | None = Header(None), x_token: list[str] | None = Header(None)):
    return {"ads_id": ads_id, "User-Agent": user_agent, "X-Token values": x_token}


@app.get("/items/{item_id}", tags=[Tags.items])
async def read_item(
    item_id: int = Path(..., title="The ID of the item to get"),
    q: str | None = Query(None, min_length=3, max_length=50, regex="^fixedquery$"), # 정규표현식
    p: str = Query(..., min_length=3), # 필수
    r: list[str] | None = Query(None), # 쿼리로 쓰러면 이렇게 명시적으로 선언해줘야 바디로 해석되는거 막음
    skip: int = 0, limit: int = 10, short: bool = False
):
    item = {"item_id": item_id, "fakeitemdb": fake_items_db[skip : skip + limit]}
    if item_id == 999:
        raise HTTPException(status_code=404, detail="Item_id 999 is dangerous!")
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


@app.post("/items/", tags=[Tags.items])
async def create_item(item: Item):
    # item.name + item.price
    return item


@app.put("/items/{item_id}", tags=[Tags.items])
async def create_item(
    item_id: int,
    item: Item = Body(
        ...,
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {
                    "name": "Bar",
                    "price": "35.4",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            },
        },
    ),
    user: User = Body(..., embed=True),
    q: str | None = None,
    importance: int = Body(..., lt=10)
):
    result = {"item_id": item_id, **item.dict(), "user": user, "importance": importance}
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



@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    for image in images:
        image.url = image.url.replace("http://", "https://")
    return images



@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights







class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


@app.post("/user/", response_model=UserOut, tags=[Tags.users], status_code = status.HTTP_201_CREATED)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved





@app.post("/login/", tags=[Tags.users])
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
