"""
异常定义模块
定义系统中使用的各种异常类
"""

class OrderManagementException(Exception):
    """订单管理系统基础异常类"""
    def __init__(self, message: str = "系统异常", code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(OrderManagementException):
    """资源未找到异常"""
    def __init__(self, resource: str = "资源"):
        message = f"{resource}未找到"
        super().__init__(message, 404)


class ValidationException(OrderManagementException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message, 400)


class AuthenticationException(OrderManagementException):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, 401)


class AuthorizationException(OrderManagementException):
    """授权异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, 403)


class BusinessException(OrderManagementException):
    """业务逻辑异常"""
    def __init__(self, message: str = "业务逻辑错误"):
        super().__init__(message, 422)


class DatabaseException(OrderManagementException):
    """数据库异常"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, 500)


class OrderNotFoundException(NotFoundException):
    """订单未找到异常"""
    def __init__(self):
        super().__init__("订单")


class ProductNotFoundException(NotFoundException):
    """产品未找到异常"""
    def __init__(self):
        super().__init__("产品")


class UserNotFoundException(NotFoundException):
    """用户未找到异常"""
    def __init__(self):
        super().__init__("用户")


class InsufficientStockException(BusinessException):
    """库存不足异常"""
    def __init__(self, product_name: str = "产品"):
        message = f"{product_name}库存不足"
        super().__init__(message)


class InvalidOrderStatusException(BusinessException):
    """无效订单状态异常"""
    def __init__(self, status: str = "状态"):
        message = f"无效的订单状态: {status}"
        super().__init__(message)


class DuplicateResourceException(BusinessException):
    """重复资源异常"""
    def __init__(self, resource: str = "资源"):
        message = f"{resource}已存在"
        super().__init__(message)


class PaymentException(BusinessException):
    """支付异常"""
    def __init__(self, message: str = "支付失败"):
        super().__init__(message)