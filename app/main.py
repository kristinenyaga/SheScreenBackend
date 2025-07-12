from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from users import models
from users.db import engine
from users.routes import router as users_routes
from messages.routes import router as messages_routes
from resources.routes import router as resource_routes
from care_plan.routes import router as care_plan_routes
from patients.routes import router as patient_routes
from patient_profiles.routes import router as patient_profiles_routes
from recommended_action.routes import router as recommended_action_routes
from service.routes import router as service_routes
from service_resource_requirement.routes import router as service_resource_requirement_routes
from service_cost.routes import router as service_cost_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(care_plan_routes)
app.include_router(resource_routes)
app.include_router(messages_routes)
app.include_router(patient_routes)
app.include_router(patient_profiles_routes)
app.include_router(recommended_action_routes)
app.include_router(service_cost_routes)
app.include_router(service_routes)
app.include_router(service_resource_requirement_routes)
app.include_router(users_routes)




if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1", port=8000,
        reload=True
    )
