# 导入业务层
from dao.order_dao import OrderDAO
# 导入数据层
from sqlalchemy.orm import Session
# 导入前端传参
from schema.order_schema import OrderCreate,OrderUpdate
# 导入模型订单层
from model.order_info import Order
# 导入时间
from datetime import datetime 
# 导入抛出异常
from fastapi import HTTPException

class OrderService:
    """
    业务逻辑层
    """
    @staticmethod
    def query_order(db:Session,order_id:int,current_user_id:int) ->None|Order:
        """
        查询id订单
        :order: 调用OrderDAO筛选
        :return: 查不到到返回异常,防止系统崩溃以及防护
        """
        order = OrderDAO.query_order(db,order_id)
        if not order:
            raise HTTPException(status_code=404,detail="订单不存在")
        if order.user_id!=current_user_id:
            raise HTTPException(status_code=403,detail="你无权限查看此订单")
        return order

    @staticmethod
    def query_list(db:Session,page: int = 1, size:int = 10):
        if page<1:
            page =1

        if size>100:
            size=100









