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
    def query_order(db:Session,order_id:int,*,include_deleted:bool=False,only_deleted:bool=False) ->Order|None:
        """
        根据订单ID查询订单。

        :param db: 数据库会话
        :param order_id: 订单ID
        :param include_deleted: 是否包含软删除订单
        :param only_deleted: 仅查询软删除订单
        :return: 订单实体,不存在则返回None
        """
        query = db.query(Order).filter(Order.id == order_id)
        if only_deleted:
            query = query.filter(Order.is_delete == 1)
        elif not include_deleted:
            query = query.filter(Order.is_delete == 0)
        return query.first()
    
    @staticmethod
    def list_order(db:Session,page: int = 1, size: int = 10, user_id: int | None = None) ->dict:
        """
        分页查询订单列表
        :param page: 第几页(默认第1页)
        :param size: 每页显示几条(默认10条)
        :param user_id: 可选的用户ID过滤
        :return 字典(包含分页信息+当前页数据列表)
        """
        skip = (page-1)*size
        query = db.query(Order).filter(Order.is_delete == 0)
        if user_id is not None:
            query = query.filter(Order.user_id == user_id)
        order_list = query.offset(skip).limit(size).all()
        total = query.count()
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
        :param order_create: 订单创建数据
        :return: 返回订单对象
        """
        date = order_create.model_dump()
        date["created_at"] = dt.now()
        date["is_delete"] = 0
        order = Order(**date)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def update_order(db:Session,order_id:int,order_update: OrderUpdate) ->Order|None:
        """
        根据ID更新订单信息
        :param db: 数据库会话
        :param order_id: 订单ID
        :param order_update: 更新数据
        :return: 更新后的订单对象，订单不存在返回 None
        """
        order = db.query(Order).filter(Order.id == order_id, Order.is_delete == 0).first()
        if not order:
            return None
        update_data = order_update.model_dump(exclude_unset=True)
        if not update_data:
            return order
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
        order = db.query(Order).filter(Order.id == order_id,Order.is_delete == 0).first()
        if not order:
            return False
        order.is_delete = 1
        order.delete_time = dt.now()
        db.commit()
        return True
    
    @staticmethod
    def deleted_list(db:Session,page: int = 1, size: int = 10, user_id: int | None = None) ->dict:
        """
        分页查询【回收站】的订单（只查已经软删除的订单）
        :param db: 数据库会话
        :param page: 当前第几页,默认第1页
        :param size: 每页显示多少条,默认10条
        :param user_id: 可选的用户ID过滤
        :return: 分页数据（列表+页码+总数+总页数）
        """
        skip = (page-1)*size
        query = db.query(Order).filter(Order.is_delete == 1)
        if user_id is not None:
            query = query.filter(Order.user_id == user_id)
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
        :param order: 筛选id以及is_delete是否为True
        :param order.is_delete: 恢复数据,取消删除标记
        :param delete_time: 清除时间
        return 恢复成功返回True,订单不存在返回False
        """
        order = db.query(Order).filter(Order.id == order_id,Order.is_delete == 1).first()
        if not order:
            return False
        order.is_delete = 0
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
    
    @staticmethod
    def query_by_order_no(db:Session,order_no:str) ->Order|None:
        """
        查重数据
        :return: 只查重未删除的
        """
        return db.query(Order).filter(Order.order_no == order_no,Order.is_delete == 0).first()