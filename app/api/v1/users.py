from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate,UserOutput,UserLogin,Token
from app.services.user_service import register_user,login_user
from app.api.deps import get_current_user

router=APIRouter()

'''
200 ok:请求成功
201 Created：请求成功，并且创建了新的资源
'''
@router.post("/register",response_model=UserOutput,status_code=status.HTTP_201_CREATED)
def register(payload:UserCreate,db:Session=Depends(get_db)):
    try:
        user=register_user(db,payload)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

#from app.schemas.user import UserLogin,Token
@router.post("/login",response_model=Token,status_code=status.HTTP_200_OK)
def login(payload:UserLogin,db:Session=Depends(get_db)):
    try:
        result=login_user(
            db,
            email=payload.email,
            password=payload.password
        )

        return{
            "access_token":result["access_token"],
            "token_type":result["token_type"]
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

#创建受保护的个人信息接口/me
@router.get("/me",response_model=UserOutput)
def get_me(current_user=Depends(get_current_user)):
    return current_user