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
    def list_order(db:Session,page: int = 1, size: int = 10) ->dict:
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
    def delete_order(db:Session,order_id:int) ->bool:
        """
        软删除,仅为标记
        :param db: 数据会话
        :param order: 筛选id以及is_datete是否为false
        :return 删除成功返回True不成功为False
        """
        order = db.query(Order).filter(Order.id == order_id,Order.is_delete == False).first()
        if not order:
            return False
        order.is_delete = True
        order.delete_time = dt.now()
        db.commit()
        return True
    
    @staticmethod
    def deleted_list(db:Session,page: int = 1, size: int = 10) ->dict:
        """
        分页查询【回收站】的订单（只查已经软删除的订单）
        :param db: 数据库会话
        :param page: 当前第几页,默认第1页
        :param size: 每页显示多少条,默认10条
        :return: 分页数据（列表+页码+总数+总页数）
        """
        skip = (page-1)*size
        query = db.query(Order).filter(Order.is_delete == True)
        order_list = query.offset(skip).limit(size).all()
        total = query.count()
        total_pages = (total+size-1)//size
        return {
            "list" : order_list, # 当前订单数据
            "page" : page, # 当前页码
            "size" : size, # 每页多少条
            "total" : total, # 回收站总条数
            "total_pages" : total_pages # 一共多少页
        }
    @staticmethod
    def restore_order(db:Session,order_id:int) ->bool:
        """
        恢复已删除的数据
        :param db: 数据会话
        :param order: 筛选id以及is_datete是否为True
        :param order.is_delete: 恢复数据,取消删除标记
        :param dalete_time: 清除时间
        return 恢复成功返回True,订单不存在返回False
        """
        order = db.query(Order).filter(Order.id == order_id,Order.is_delete == True).first()
        if not order:
            return False
        order.is_delete = False
        order.delete_time = None
        db.commit()
        return True

    @staticmethod
    def hard_order(db:Session,order_id:int) ->bool:
        """
        永久删除数据(不能恢复)
        :param db: 数据库会话
        :param order: 筛选id
        :return: 等于则delete删除,不等于则False
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
        db.delete(order)
        db.commit()
        return True