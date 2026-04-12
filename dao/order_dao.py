# 导入数据库
from sqlalchemy.orm import Session
# 导入订单表
from model.order_info import Order
# 导入前端传参
from schema.order_schema import OrderCreate,OrderUpdate
# 导入时间
from datetime import datetime as dt

class OrderDAO:
    @staticmethod
    def query_order(db:Session,order_id:int) ->Order|None:
        """
        根据订单ID查询单个订单
        :param db: 数据库会话
        :param order_id: 订单ID
        :return: 订单实体,不存在则返回None
        """
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def list_order(db:Session,page: int = 1, size: int = 10):
        """
        分页查询订单列表
        :param page: 第几页(默认第1页)
        :param size: 每页显示几条(默认10条)
        :return 字典(包含分页信息+当前页数据列表)
        """
        skip = (page-1)*size
        order_list = db.query(Order).offset(skip).limit(size).all()
        total = db.query(Order).count()
        total_pages = (total+size -1) //size
        return {
            "list" : order_list, # 当前页数据
            "page" : page, # 当前页码
            "size" : size, # 每页条数
            "total" : total,  # 总条数
            "total_pages" : total_pages #总页数
        }

    @staticmethod
    def create_order(db:Session,order_create:OrderCreate) ->Order:
        """
        创建订单
        :date: 将订单数据转换成字典
        :create_time: 创建时间
        :update_time: 更新时间
        :order: 将字典拆包,装进数据库订单时间
        :db.add: 准备保存到数据库
        :db.commit: 真正提交保存（永久写入）
        :db.refresh: 刷新,获取最新数据(包括自增ID)
        :return: 返回订单
        """
        date = order_create.model_dump()
        date["create_time"] = dt.now()
        date["update_time"] = dt.now()
        order = Order(**date)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def update_order(db:Session,order_id:int,order_update: OrderUpdate) ->Order|None:
        """
        ID修改订单
        :param db: 数据库会话
        :param order_id: 要删除的订单ID
        :return: 删除成功返回True,订单不存在/删除失败返回False
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        update_data = order_update.model_dump(exclude_unset=True)
        update_data["update_time"] = dt.now()
        for key,value in update_data.items():
            setattr(order,key,value)
        db.commit() 
        db.refresh(order)
        return order
    @staticmethod
    def delete_order(db:Session,order_id:int):






