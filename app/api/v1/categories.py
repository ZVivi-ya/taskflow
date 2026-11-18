from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryOutput,
    CategoryUpdate,
)
from app.services import category as category_service


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "",
    response_model=CategoryOutput,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.create_category(
        db=db,
        payload=payload,
        owner_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[CategoryOutput],
)
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.get_categories(
        db=db,
        owner_id=current_user.id,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryOutput,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.get_category(
        db=db,
        category_id=category_id,
        owner_id=current_user.id,
    )


@router.patch(
    "/{category_id}",
    response_model=CategoryOutput,
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.update_category(
        db=db,
        category_id=category_id,
        payload=payload,
        owner_id=current_user.id,
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category_service.delete_category(
        db=db,
        category_id=category_id,
        owner_id=current_user.id,
    )

    return None