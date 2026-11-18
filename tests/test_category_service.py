import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    EmptyCategoryUpdateError,
    InvalidCategoryUpdateError,
)
from app.models.category import Category
from app.models.user import User
from app.repositories import category as category_repository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services import category as category_service


def test_service_create_list_get_update_and_delete(
    db_session,
    category_owners,
):
    owner_id = category_owners[0].id
    created = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="工作", description="项目相关"),
        owner_id=owner_id,
    )

    assert isinstance(created, Category)
    assert created.id is not None
    assert created.owner_id == owner_id
    assert category_service.get_categories(
        db_session,
        owner_id=owner_id,
    ) == [created]
    assert category_service.get_category(
        db_session,
        category_id=created.id,
        owner_id=owner_id,
    ) == created

    updated = category_service.update_category(
        db_session,
        category_id=created.id,
        payload=CategoryUpdate(description="更新后的描述"),
        owner_id=owner_id,
    )
    assert updated.name == "工作"
    assert updated.description == "更新后的描述"

    category_service.delete_category(
        db_session,
        category_id=created.id,
        owner_id=owner_id,
    )
    with pytest.raises(CategoryNotFoundError):
        category_service.get_category(
            db_session,
            category_id=created.id,
            owner_id=owner_id,
        )


def test_service_rejects_duplicate_name_and_rolls_back(
    db_session,
    category_owners,
):
    owner_id = category_owners[0].id
    category_service.create_category(
        db_session,
        payload=CategoryCreate(name="唯一"),
        owner_id=owner_id,
    )

    with pytest.raises(CategoryNameAlreadyExistsError):
        category_service.create_category(
            db_session,
            payload=CategoryCreate(name="唯一"),
            owner_id=owner_id,
        )

    assert len(category_repository.get_all(db_session, owner_id=owner_id)) == 1


def test_service_preserves_foreign_key_error_and_session_remains_usable(
    db_session,
):
    with pytest.raises(IntegrityError) as exc_info:
        category_service.create_category(
            db_session,
            payload=CategoryCreate(name="无效 owner"),
            owner_id=999999,
        )

    assert exc_info.value.orig.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY"

    recovered_owner = User(
        username="category_recovered_owner",
        nickname="Recovered",
        email="category_recovered_owner@example.com",
        password_hash="test-hash",
    )
    db_session.add(recovered_owner)
    db_session.commit()

    created = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="回滚后正常创建"),
        owner_id=recovered_owner.id,
    )
    assert created.name == "回滚后正常创建"
    assert created.owner_id == recovered_owner.id


def test_service_rejects_duplicate_name_on_update_and_rolls_back(
    db_session,
    category_owners,
):
    owner_id = category_owners[0].id
    first = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="第一类"),
        owner_id=owner_id,
    )
    second = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="第二类"),
        owner_id=owner_id,
    )

    with pytest.raises(CategoryNameAlreadyExistsError):
        category_service.update_category(
            db_session,
            category_id=second.id,
            payload=CategoryUpdate(name=first.name),
            owner_id=owner_id,
        )

    db_session.expire_all()
    assert category_repository.get_by_id(
        db_session,
        category_id=second.id,
        owner_id=owner_id,
    ).name == "第二类"


def test_service_preserves_non_unique_update_integrity_error(
    db_session,
    category_owners,
    monkeypatch,
):
    category = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="待更新"),
        owner_id=category_owners[0].id,
    )

    def update_with_invalid_owner(db, *, category, update_data):
        category.owner_id = 999999
        db.flush()
        return category

    monkeypatch.setattr(
        category_service.category_repository,
        "update",
        update_with_invalid_owner,
    )

    with pytest.raises(IntegrityError) as exc_info:
        category_service.update_category(
            db_session,
            category_id=category.id,
            payload=CategoryUpdate(description="触发外键失败"),
            owner_id=category_owners[0].id,
        )

    assert exc_info.value.orig.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY"

    db_session.expire_all()
    persisted = category_repository.get_by_id(
        db_session,
        category_id=category.id,
        owner_id=category_owners[0].id,
    )
    assert persisted is not None
    assert persisted.name == "待更新"


def test_service_rejects_empty_update(db_session, category_owners):
    category = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="待更新"),
        owner_id=category_owners[0].id,
    )

    with pytest.raises(EmptyCategoryUpdateError):
        category_service.update_category(
            db_session,
            category_id=category.id,
            payload=CategoryUpdate(),
            owner_id=category_owners[0].id,
        )


def test_service_rejects_null_name_update(db_session, category_owners):
    category = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="待更新"),
        owner_id=category_owners[0].id,
    )

    with pytest.raises(InvalidCategoryUpdateError):
        category_service.update_category(
            db_session,
            category_id=category.id,
            payload=CategoryUpdate(name=None),
            owner_id=category_owners[0].id,
        )


def test_service_rejects_missing_or_foreign_category(
    db_session,
    category_owners,
):
    category = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="Alice 分类"),
        owner_id=category_owners[0].id,
    )

    for category_id, owner_id in (
        (999999, category_owners[0].id),
        (category.id, category_owners[1].id),
    ):
        with pytest.raises(CategoryNotFoundError):
            category_service.get_category(
                db_session,
                category_id=category_id,
                owner_id=owner_id,
            )


def test_service_rolls_back_unexpected_create_error(
    db_session,
    category_owners,
    monkeypatch,
):
    real_create = category_service.category_repository.create

    def create_then_fail(db, **kwargs):
        real_create(db, **kwargs)
        raise RuntimeError("simulated create failure")

    monkeypatch.setattr(
        category_service.category_repository,
        "create",
        create_then_fail,
    )

    with pytest.raises(RuntimeError, match="simulated create failure"):
        category_service.create_category(
            db_session,
            payload=CategoryCreate(name="必须回滚"),
            owner_id=category_owners[0].id,
        )

    assert category_repository.get_all(
        db_session,
        owner_id=category_owners[0].id,
    ) == []


def test_service_rolls_back_unexpected_update_error(
    db_session,
    category_owners,
    monkeypatch,
):
    category = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="原始名称"),
        owner_id=category_owners[0].id,
    )
    real_update = category_service.category_repository.update

    def update_then_fail(db, **kwargs):
        real_update(db, **kwargs)
        raise RuntimeError("simulated update failure")

    monkeypatch.setattr(
        category_service.category_repository,
        "update",
        update_then_fail,
    )

    with pytest.raises(RuntimeError, match="simulated update failure"):
        category_service.update_category(
            db_session,
            category_id=category.id,
            payload=CategoryUpdate(name="不得持久化"),
            owner_id=category_owners[0].id,
        )

    db_session.expire_all()
    assert category_repository.get_by_id(
        db_session,
        category_id=category.id,
        owner_id=category_owners[0].id,
    ).name == "原始名称"


def test_service_rolls_back_unexpected_delete_error(
    db_session,
    category_owners,
    monkeypatch,
):
    category = category_service.create_category(
        db_session,
        payload=CategoryCreate(name="不得删除"),
        owner_id=category_owners[0].id,
    )
    real_delete = category_service.category_repository.delete

    def delete_then_fail(db, **kwargs):
        real_delete(db, **kwargs)
        raise RuntimeError("simulated delete failure")

    monkeypatch.setattr(
        category_service.category_repository,
        "delete",
        delete_then_fail,
    )

    with pytest.raises(RuntimeError, match="simulated delete failure"):
        category_service.delete_category(
            db_session,
            category_id=category.id,
            owner_id=category_owners[0].id,
        )

    db_session.expire_all()
    assert category_repository.get_by_id(
        db_session,
        category_id=category.id,
        owner_id=category_owners[0].id,
    ) is not None
