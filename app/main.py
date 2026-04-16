#==============项目入口=============
from fastapi import FastAPI
from core.db import Base, engine
from core.logger import logger
from api import user_api, product_api, order_api, stock_api

# 创建表
Base.metadata.create_all(bind=engine)
logger.info('FastAPI application initialized.')

app = FastAPI(title="订单管理系统")

# 路由
app.include_router(user_api.router, prefix="/api/user", tags=["用户"])
app.include_router(product_api.router, prefix="/api/product", tags=["商品"])
app.include_router(order_api.router, prefix="/api/order", tags=["订单"])
app.include_router(stock_api.router, prefix="/api/stock", tags=["库存"])

@app.get("/")
def index():
    return {"msg": "order management system running"}
