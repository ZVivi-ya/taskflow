import pytest
from pydantic import ValidationError

from app.models.category import Category
from app.repositories import category as category_repository
from app.schemas.category import CategoryCreate, CategoryOutput, CategoryUpdate


def test_category_create_accepts_valid_data():
    payload = CategoryCreate(name="学习", description="学习相关任务")

    assert payload.name == "学习"
    assert payload.description == "学习相关任务"


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"name": ""},
        {"name": "x" * 51},
        {"name": 123},
        {"name": "学习", "description": []},
    ],
)
def test_category_create_rejects_invalid_data(data):
    with pytest.raises(ValidationError):
        CategoryCreate.model_validate(data)


def test_category_create_description_is_optional_and_nullable():
    assert CategoryCreate(name="学习").description is None
    assert CategoryCreate(name="学习", description=None).description is None


def test_category_update_field_validation():
    assert CategoryUpdate().model_dump(exclude_unset=True) == {}
    assert CategoryUpdate(name=None).model_dump(exclude_unset=True) == {
        "name": None
    }

    for data in ({"name": ""}, {"name": "x" * 51}, {"name": 123}):
        with pytest.raises(ValidationError):
            CategoryUpdate.model_validate(data)


def test_category_output_serializes_orm_object(db_session, category_owners):
    category = category_repository.create(
        db_session,
        owner_id=category_owners[0].id,
        name="ORM 分类",
        description=None,
    )
    db_session.commit()
    db_session.refresh(category)

    output = CategoryOutput.model_validate(category)

    assert isinstance(category, Category)
    assert output.id == category.id
    assert output.name == "ORM 分类"
    assert output.description is None
    assert output.owner_id == category_owners[0].id
    assert output.created_at == category.created_at
    assert output.updated_at == category.updated_at
