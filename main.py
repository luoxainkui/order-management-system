"""
项目入口文件
===========
FastAPI 应用启动入口

运行命令:
    uvicorn main:app --reload

访问地址:
    http://localhost:8000
    http://localhost:8000/docs  (Swagger文档)
"""
from fastapi import FastAPI
from core.db import Base, engine
from core.error_handler import register_error_handlers
from api import product_api, order_api, user_api, stock_api


# ======================================================================
# 创建数据库表
# ======================================================================
# 程序启动时自动创建所有表
# 表结构从 model 层自动映射
Base.metadata.create_all(bind=engine)


# ======================================================================
# 初始化 FastAPI 应用
# ======================================================================
app = FastAPI(
    title="订单管理系统 API",
    description="基于 FastAPI + SQLAlchemy 的分层架构订单管理系统",
    version="1.0.0"
)


# ======================================================================
# 注册全局异常降级处理器
# ======================================================================
# 这就是"异常降级"的核心：所有Service层抛出的异常
# 自动被这里捕获，转成标准HTTP响应
register_error_handlers(app)


# ======================================================================
# 注册路由
# ======================================================================
app.include_router(product_api.router)
app.include_router(order_api.router)
app.include_router(user_api.router)
app.include_router(stock_api.router)


# ======================================================================
# 健康检查接口
# ======================================================================
@app.get("/health", summary="健康检查")
def health_check():
    return {
        "code": 200,
        "msg": "服务运行正常",
        "data": {
            "status": "ok",
            "version": "1.0.0"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
