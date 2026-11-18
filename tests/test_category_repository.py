import pytest
from sqlalchemy.exc import IntegrityError

from app.models.category import Category
from app.repositories import category as category_repository


def test_repository_create_get_update_and_delete(
    db_session,
    category_owners,
):
    owner_id = category_owners[0].id
    category = category_repository.create(
        db_session,
        owner_id=owner_id,
        name="待办",
        description="初始描述",
    )
    db_session.commit()

    assert isinstance(category, Category)
    assert category.id is not None
    assert category.owner_id == owner_id
    assert category_repository.get_by_id(
        db_session,
        category_id=category.id,
        owner_id=owner_id,
    ) == category

    updated = category_repository.update(
        db_session,
        category=category,
        update_data={"name": "已完成", "description": None},
    )
    db_session.commit()

    assert updated.name == "已完成"
    assert updated.description is None

    category_repository.delete(db_session, category=updated)
    db_session.commit()

    assert category_repository.get_by_id(
        db_session,
        category_id=category.id,
        owner_id=owner_id,
    ) is None


def test_repository_get_by_id_filters_by_owner(db_session, category_owners):
    category = category_repository.create(
        db_session,
        owner_id=category_owners[0].id,
        name="Alice 私有分类",
    )
    db_session.commit()

    assert category_repository.get_by_id(
        db_session,
        category_id=category.id,
        owner_id=category_owners[1].id,
    ) is None
    assert category_repository.get_by_id(
        db_session,
        category_id=999999,
        owner_id=category_owners[0].id,
    ) is None


def test_repository_get_all_filters_owner_and_orders_results(
    db_session,
    category_owners,
):
    owner_a_id, owner_b_id = (owner.id for owner in category_owners)
    first = category_repository.create(
        db_session,
        owner_id=owner_a_id,
        name="第一类",
    )
    second = category_repository.create(
        db_session,
        owner_id=owner_a_id,
        name="第二类",
    )
    category_repository.create(
        db_session,
        owner_id=owner_b_id,
        name="另一用户分类",
    )
    db_session.commit()

    categories = category_repository.get_all(
        db_session,
        owner_id=owner_a_id,
    )

    assert [category.id for category in categories] == [
        second.id,
        first.id,
    ]
    assert all(category.owner_id == owner_a_id for category in categories)


def test_repository_unique_name_constraint_is_scoped_to_owner(
    db_session,
    category_owners,
):
    category_repository.create(
        db_session,
        owner_id=category_owners[0].id,
        name="相同名称",
    )
    category_repository.create(
        db_session,
        owner_id=category_owners[1].id,
        name="相同名称",
    )
    db_session.commit()

    with pytest.raises(IntegrityError):
        category_repository.create(
            db_session,
            owner_id=category_owners[0].id,
            name="相同名称",
        )

    db_session.rollback()


def test_repository_enforces_owner_foreign_key(db_session):
    with pytest.raises(IntegrityError):
        category_repository.create(
            db_session,
            owner_id=999999,
            name="无效用户分类",
        )

    db_session.rollback()
