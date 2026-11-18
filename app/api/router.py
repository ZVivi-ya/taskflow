from fastapi import APIRouter
from app.api.v1.users import router as users_router
from app.api.v1 import tasks,categories

api_router=APIRouter()

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["用户"]
)

api_router.include_router(tasks.router)
api_router.include_router(categories.router)