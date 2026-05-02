"""
全局统一异常体系
===============
工业级异常分层设计，这是非常重要的架构设计！

为什么不直接用print/raise?
  1. 异常类型 = 错误语义，看到异常类型就知道哪一层错了
  2. 全局异常处理器统一捕获，前端拿到统一格式
  3. 不同错误码便于做监控告警统计

异常分层设计原则（从粗到细）：
  400 = 参数校验失败   →  前端传参错了
  401 = 未登录        →  用户没登录
  403 = 无权限        →  登录了但不让操作
  404 = 资源不存在    →  查的ID根本不存在
  422 = 业务错误      →  参数都对，但业务规则不允许（重复、库存不足等）
  500 = 系统错误      →  数据库崩了/代码bug
"""


class BusinessBaseException(Exception):
    """
    【所有自定义异常的根父类】
    全局异常处理器只捕获这个子类,其他普通Python异常算系统500错误
    
    设计思想：面向对象的多态
    只要是继承我的,统一格式返回,不用写N个except
    """
    def __init__(self, message: str, code: int = 400):
        self.message = message  # 给人看的错误文案
        self.code = code        # 给代码/监控看的错误码
        super().__init__(self.message)


class NotFoundException(BusinessBaseException):
    """
    404 资源不存在
    使用场景:查数据库返回None时抛出
    例："商品不存在"、"订单已被删除"
    """
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, 404)


class ValidationException(BusinessBaseException):
    """
    400 参数校验失败
    使用场景:Service层主动做的业务参数校验
    例："名称不能为空"、"价格不能小于0"
    
    注意:和Pydantic Schema校验的区别
          Schema是入口的格式校验,这个是业务规则校验
    """
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(message, 400)


class UnauthorizedException(BusinessBaseException):
    """
    401 未认证/未登录
    使用场景:token无效、token过期、没传token
    前端收到401应该自动跳转到登录页
    """
    def __init__(self, message: str = "未授权，请登录"):
        super().__init__(message, 401)


class ForbiddenException(BusinessBaseException):
    """
    403 权限不足
    使用场景：用户登录了，但这个数据不是他的
    例:A用户想修改B用户的订单
    """
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, 403)


class BusinessException(BusinessBaseException):
    """
    422 业务规则不允许
    最常用的业务异常！参数都对，但逻辑上行不通
    例："商品名称重复"、"库存不足"、"订单已支付不能修改"
    
    这是区分"参数错误"和"业务错误"的关键分界
    """
    def __init__(self, message: str = "业务处理失败"):
        super().__init__(message, 422)


class DatabaseException(BusinessBaseException):
    """
    500 数据库异常
    非常严重的错误,监控系统应该专门告警这个code
    正常业务代码永远不应该走到这里
    """
    def __init__(self, message: str = "数据库操作异常"):
        super().__init__(message, 500)
