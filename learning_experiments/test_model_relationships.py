from sqlalchemy.orm import configure_mappers

from app.models import User, Task, Category, TaskCategory


# 1. 配置并检查所有 ORM Relationships
configure_mappers()

print("1. ORM Relationships 配置成功")


# 2. 创建一个 User 对象
user = User(
    username="relationship_test",
    email="relationship_test@example.com",
    password_hash="test_hash",
)

# 3. 创建一个 Task，并指定所属用户
task = Task(
    title="学习 SQLAlchemy Relationships",
    owner=user,
)

# 4. 创建一个 Category，并指定所属用户
category = Category(
    name="学习",
    owner=user,
)

# 5. 创建任务和分类之间的关联对象
task_category = TaskCategory(
    task=task,
    category=category,
)


# 6. 验证 User 和 Task 的关系
assert task.owner is user
assert task in user.tasks

print("2. User ↔ Task 关系正常")


# 7. 验证 User 和 Category 的关系
assert category.owner is user
assert category in user.categories

print("3. User ↔ Category 关系正常")


# 8. 验证 Task 和 TaskCategory 的关系
assert task_category in task.task_categories
assert task_category.task is task

print("4. Task ↔ TaskCategory 关系正常")


# 9. 验证 Category 和 TaskCategory 的关系
assert task_category in category.task_categories
assert task_category.category is category

print("5. Category ↔ TaskCategory 关系正常")


print("\n所有 ORM Relationships 测试通过！")