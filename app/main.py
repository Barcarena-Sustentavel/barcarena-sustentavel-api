from fastapi import FastAPI
from app.api.v1.endpoints.dimensoes import router

app = FastAPI()
app.include_router(router)

def print_hi(name):
    print(f'Hi, {name}')

if __name__ == '__main__':
   
    print_hi('PyCharm')

