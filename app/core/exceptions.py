
# app/core/exceptions.py


# =========================
# 统一业务异常基类
# =========================

class AppException(Exception):
    """
    所有 TaskFlow 业务异常的基类。

    status_code: 对应的 HTTP 状态码
    error_code: 业务错误编码
    default_message: 默认错误信息
    """

    status_code = 500
    error_code = "INTERNAL_ERROR"
    default_message = "服务器内部错误"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


# =========================
# 任务相关异常
# =========================

class TaskNotFoundError(AppException):
    """任务不存在，或者当前用户无权访问该任务。"""

    status_code = 404
    error_code = "TASK_NOT_FOUND"
    default_message = "任务不存在"


class InvalidTaskUpdateError(AppException):
    """任务更新字段不符合业务规则。"""

    status_code = 422
    error_code = "INVALID_TASK_UPDATE"
    default_message = "任务更新字段不合法"


class EmptyTaskUpdateError(AppException):
    """客户端没有提供任何需要更新的字段。"""

    status_code = 400
    error_code = "EMPTY_TASK_UPDATE"
    default_message = "更新内容不能为空"


# =========================
# 用户相关异常
# =========================

class InvalidCredentialsError(AppException):
    """用户邮箱或密码错误。"""

    status_code = 401
    error_code = "INVALID_CREDENTIALS"
    default_message = "邮箱或密码错误"


class EmailAlreadyExistsError(AppException):
    """邮箱已经注册。"""

    status_code = 409
    error_code = "EMAIL_ALREADY_EXISTS"
    default_message = "该邮箱已经注册"


class UsernameAlreadyExistsError(AppException):
    """用户名已经被使用。"""

    status_code = 409
    error_code = "USERNAME_ALREADY_EXISTS"
    default_message = "该用户名已经被使用"


# =========================
# 分类相关异常
# =========================

class CategoryNotFoundError(AppException):
    """分类不存在，或者当前用户无权访问该分类。"""

    status_code = 404
    error_code = "CATEGORY_NOT_FOUND"
    default_message = "分类不存在"


class CategoryNameAlreadyExistsError(AppException):
    """当前用户下已经存在同名分类。"""

    status_code = 409
    error_code = "CATEGORY_NAME_ALREADY_EXISTS"
    default_message = "分类名称已经存在"


class EmptyCategoryUpdateError(AppException):
    """分类更新内容为空。"""

    status_code = 400
    error_code = "EMPTY_CATEGORY_UPDATE"
    default_message = "分类更新内容不能为空"


class InvalidCategoryUpdateError(AppException):
    """分类更新字段不符合业务规则。"""

    status_code = 422
    error_code = "INVALID_CATEGORY_UPDATE"
    default_message = "分类更新字段不合法"


# =========================
# 任务-分类关联相关异常
# =========================

class TaskCategoryLinkNotFoundError(AppException):
    """任务与分类之间的关联不存在。"""

    status_code = 404
    error_code = "TASK_CATEGORY_LINK_NOT_FOUND"
    default_message = "任务与分类的关联不存在"


class TaskCategoryLinkConflictError(AppException):
    """任务与分类关联发生冲突。"""

    status_code = 409
    error_code = "TASK_CATEGORY_LINK_CONFLICT"
    default_message = "任务与分类关联冲突"
