# 导入数据库
from sqlalchemy.orm import Session
# 导入订单表
from model.order_info import Order
# 导入前端传参
from schema.order_schema import OrderCreate

class OrderDAO:
    @staticmethod
    def query_order(db:Session,order_id:int):
        """查询订单"""
        return db.query(Order).filter(Order.id == order_id).first()