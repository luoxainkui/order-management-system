"""
全局异常降级处理器
==================
"异常降级"

所有自定义异常都会被这里捕获，自动转成标准的HTTP响应格式
不用在每个接口里写 try-except
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.exception import (
    BusinessBaseException,
    ValidationException,
    BusinessException,
    NotFoundException,
    ForbiddenException,
    UnauthorizedException
)
from core.logger import get_logger
import time


logger = get_logger("error_handler")


# ======================================================================
# HTTP 状态码映射
# ======================================================================

EXCEPTION_HTTP_STATUS = {
    ValidationException: 400,    # 参数错误 → 400 Bad Request
    BusinessException: 400,      # 业务错误 → 400 Bad Request
    NotFoundException: 404,      # 资源不存在 → 404 Not Found
    ForbiddenException: 403,     # 权限不足 → 403 Forbidden
    UnauthorizedException: 401,  # 未登录 → 401 Unauthorized
}


def register_error_handlers(app: FastAPI):
    """
    注册全局异常处理器到FastAPI应用
    
    在 main.py 里调用:
        from core.error_handler import register_error_handlers
        register_error_handlers(app)
    
    之后所有接口抛出的自定义异常都会被自动降级处理!
    """

    @app.exception_handler(BusinessBaseException)
    async def base_exception_handler(request: Request, exc: BusinessBaseException):
        """
        自定义异常降级处理
        
        所有继承自BaseException的异常都会走到这里
        自动转成标准的JSON响应格式
        """
        status_code = EXCEPTION_HTTP_STATUS.get(type(exc), 400)
        
        logger.warning(f"[{status_code}] {exc.message}")
        
        return JSONResponse(
            status_code=status_code,
            content={
                "code": exc.code,
                "msg": exc.message,
                "data": None,
                "timestamp": int(time.time())
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        全局兜底异常处理器
        
        所有没捕获到的异常最后都会走到这里
        防止系统500崩溃, 给前端友好提示
        """
        logger.error(f"未捕获异常: {type(exc).__name__}: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "msg": "服务器繁忙, 请稍后重试",
                "data": None,
                "timestamp": int(time.time())
            }
        )
