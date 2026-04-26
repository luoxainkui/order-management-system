"""
统一全局异常
按模块拆分订单/用户/商品单独异常，文案区分业务，结构
"""

class BusinessBaseException(Exception):
    """全局自定义异常基类"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


# 通用细分异常（只按HTTP语义分，不按业务模块分）
class NotFoundException(BusinessBaseException):
    """资源不存在 404"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, 404)


class ValidationException(BusinessBaseException):
    """参数校验失败 400"""
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(message, 400)


class UnauthorizedException(BusinessBaseException):
    """未登录认证 401"""
    def __init__(self, message: str = "未授权，请登录"):
        super().__init__(message, 401)


class ForbiddenException(BusinessBaseException):
    """权限不足 403"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, 403)


class BusinessException(BusinessBaseException):
    """通用业务异常 422(重复、库存、状态错误、操作失败全走这个)"""
    def __init__(self, message: str = "业务处理失败"):
        super().__init__(message, 422)


class DatabaseException(BusinessBaseException):
    """数据库异常 500"""
    def __init__(self, message: str = "数据库操作异常"):
        super().__init__(message, 500)