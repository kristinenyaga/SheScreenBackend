from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from users import models
from users.db import engine
from users.routes import router as users_routes
from messages.routes import router as messages_routes
from facility.routes import router as facility_routes
from facility_user.routes import router as facility_user_routes


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(users_routes)
app.include_router(messages_routes)
app.include_router(facility_routes)
app.include_router(facility_user_routes)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1", port=8000,
        reload=True
    )
