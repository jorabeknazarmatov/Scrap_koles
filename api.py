from fastapi import FastAPI
from db import crud
from schemas import Product
import uvicorn

app = FastAPI()


@app.get(path="/all", summary="Все товары", tags=["Товары"])
def all_products():
    return crud.all_products()


@app.post(path="/product/add", summary="Добавить товар", tags=['Товары'])
def add_product(product: Product):
    pass
    

def main():
    uvicorn.run('main:app', reload=True)
