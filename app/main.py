from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from users import models
from users.db import engine
from users.routers import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1", port=8000,
        reload=True
    )
