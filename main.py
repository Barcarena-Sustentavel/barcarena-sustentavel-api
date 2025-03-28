import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.router import router as api_router
app = FastAPI(
    title="Barcarena Sustentavel",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    #allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
    )
