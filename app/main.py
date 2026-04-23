# ===================== 路径兼容补丁（仅开发期用，正式上线可保留/移除）=====================
# 解决 core模块找不到的跨目录导入问题，不破坏任何正式架构
import sys
from pathlib import Path

# 获取当前main.py文件所在位置
CURRENT_FILE = Path(__file__).resolve()
# 定位到整个项目的最外层根目录（order-management-system）
PROJECT_ROOT = CURRENT_FILE.parent.parent
# 将项目根目录加入Python模块搜索范围，让全局可以找到core/dao/model等文件夹
sys.path.insert(0, str(PROJECT_ROOT))
# ======================================================================================

# 导入FastAPI核心组件
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# 导入全局数据库、日志工具（现在路径已经完全能识别了）
from core.db import Base, engine
from core.logger import logger
from core.exception import OrderManagementException

# 导入所有业务模块路由
from api import user_api, product_api, order_api, stock_api

# ===================== 应用初始化与数据表自动创建 =====================
# 程序启动时，自动根据Model定义在数据库中生成所有数据表
Base.metadata.create_all(bind=engine)

# 记录系统启动日志
logger.info('FastAPI 订单管理系统 应用初始化完成')

# 创建FastAPI应用实例，配置系统标题
app = FastAPI(
    title="订单管理系统",
    description="课程作业/实训项目 - 完整订单全链路管理后端",
    version="1.0.0"
)

# ===================== 全局统一异常处理器 =====================
# 全局捕获自定义业务异常，统一返回规范错误格式，前端好解析
@app.exception_handler(OrderManagementException)
async def global_business_exception_handler(request: Request, exc: OrderManagementException):
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message
        }
    )

# ===================== 注册全局业务路由 =====================
# 用户模块路由
app.include_router(user_api.router, prefix="/api/user", tags=["用户管理"])
# 商品模块路由
app.include_router(product_api.router, prefix="/api/product", tags=["商品管理"])
# 订单模块路由
app.include_router(order_api.router, prefix="/api/order", tags=["订单管理"])
# 库存模块路由
app.include_router(stock_api.router, prefix="/api/stock", tags=["库存管理"])

# ===================== 系统健康检查首页 =====================
@app.get("/", summary="系统首页/健康检测")
def system_index():
    """项目根路径，验证服务是否正常运行"""
    return {
        "code": 200,
        "msg": "订单管理系统运行正常",
        "docs": "http://127.0.0.1:8000/docs"
    }

# ===================== 服务启动与端口监听 =====================
if __name__ == "__main__":
    import uvicorn
    logger.info(" 服务开始启动,监听端口:8000")

    # 启动uvicorn服务
    uvicorn.run(
        # 指定应用实例位置
        "app.main:app",
        # 监听本机+局域网可访问
        host="0.0.0.0",
        # 端口号，默认FastAPI标准8000
        port=8000,
        # 开发模式：代码修改后自动重载，上线时改为False
        reload=True
    )