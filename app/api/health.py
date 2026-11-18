from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db

router=APIRouter()

# GET /api/v1/health :检查应用是否能够正常响应请求
@router.get("/health")
def health_check():
    return{
        "status":"ok",
        "message":"TaskFlow API is running"
    }


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "unavailable"},
        )

    return {"status": "ok", "database": "ready"}