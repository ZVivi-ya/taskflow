from sqlalchemy import inspect, text

from app.db.session import engine


with engine.connect() as connection:

    inspector = inspect(connection)

    # 1. 检查数据库中的表
    print("\n========== 1. 数据库表 ==========")

    tables = inspector.get_table_names()

    for table in tables:
        print(table)

    expected_tables = {
        "users",
        "tasks",
        "categories",
        "task_categories",
        "alembic_version",
    }

    missing_tables = expected_tables - set(tables)

    assert not missing_tables, f"缺少数据表：{missing_tables}"

    # 2. 检查 tasks 外键
    print("\n========== 2. tasks 外键 ==========")

    task_fks = inspector.get_foreign_keys("tasks")

    for fk in task_fks:
        print(fk)

    owner_fk = next(
        fk for fk in task_fks
        if fk["constrained_columns"] == ["owner_id"]
    )

    assert owner_fk["options"].get("ondelete") == "CASCADE"

    # 3. 检查分类关联表外键
    print("\n========== 3. task_categories 外键 ==========")

    association_fks = inspector.get_foreign_keys("task_categories")

    for fk in association_fks:
        print(fk)

        assert fk["options"].get("ondelete") == "CASCADE"

    # 4. 检查索引
    print("\n========== 4. task_categories 索引 ==========")

    indexes = inspector.get_indexes("task_categories")

    for index in indexes:
        print(index)

    assert any(
        index["name"] == "ix_task_categories_category_id"
        for index in indexes
    )

    # 5. 检查原有数据
    print("\n========== 5. 原有数据 ==========")

    for table in ["users", "tasks"]:
        count = connection.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar_one()

        print(f"{table}：{count} 条")

    # 6. 检查 Alembic 版本
    print("\n========== 6. Alembic 版本 ==========")

    version = connection.execute(
        text("SELECT version_num FROM alembic_version")
    ).scalar_one()

    print(version)

    assert version == "5370c94fd036"

    # 7. 检查数据库外键完整性
    print("\n========== 7. 外键完整性 ==========")

    violations = connection.execute(
        text("PRAGMA foreign_key_check")
    ).fetchall()

    print(violations)

    assert not violations, f"存在外键违规：{violations}"

    print("\n迁移验收通过！")