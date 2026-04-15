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
    def query_list(db:Session,page: None, size: None) ->Order|dict:
        """
        页面展示，分页查询
        :page: 把异常降级强制转义为1
        :size: 把异常降级强制转义为10
        """
        try:
            page = int(page) if page not in (None,"") else 1
            size = int(size) if size not in (None,"") else 10

            page = max(page,1)
            size = min(size,100)

            return OrderDAO.list_order(db,page=page,size=size)
        except Exception:
            return {"list" : [],"page" : 1,"size" : 10,"total" : 0,"total_pages" : 0}

    @staticmethod
    def deleted_list(db:Session,page: None,size: None) ->Order|dict:
        """
        页面展示,分页查询已删除的
        :page: 把异常降级强制转义为1
        :size: 把异常降级强制转义为10
        """
        try:
            page = int(page) if page not in (None,"") else 1
            size = int(size) if size not in (None,"") else 10

            page = max(page,1)
            size = min(size,10)
            
            return OrderDAO.deleted_list(db,page=page,size=size)
        except Exception:
            return {"list" : [],"page" : 1,"size" : 10,"total" : 0,"total_pages" : 0}

    @staticmethod
    def create_order(db:Session,order_create:OrderCreate,current_user_id:int) ->Order|None:
        """
        创建订单(核心,校验,查重,限制价格区间)
        :param db: 数据库连接
        :param order_create: 前端传的订单数据（已自动校验）
        :param current_user_id: 当前登录用户ID
        :return: 创建成功的订单
        """
        create = order_create.model_dump()
        total_price = create.get("total_price",0)
        if not isinstance(total_price,(int,float)) or total_price < 0 or total_price > 999999:
            raise HTTPException(status_code=400,detail="价格必须在0~999999之间")
        
        order_no = str(create.get("order_no","")).strip()
        if not order_no or len(order_no)>50:
            raise HTTPException(status_code=400,detail="订单编号不合法")
        
        exists = OrderDAO.query_by_order_no(db,order_no)
        if exists:
            raise HTTPException(status_code=400,detail="订单已经重复")

        order_create.user_id = current_user_id

        return OrderDAO.create_order(db,order_create)

    @staticmethod
    def update_order(db:Session,order_id:int,update_data:OrderUpdate,current_user_id:int)->Order:
        """
        修改订单
        未完成
        """
        order = OrderDAO.query_order(db,order_id)
        if not order:
            raise HTTPException(status_code=404,detail="订单不存在")
        if order.user_id != current_user_id:
            raise HTTPException(status_code=403,detail="无权修改此订单")
        
        date = update_data.model_dump(exclude=True)

        if "total_price" in date:
            price = date["total_price"]
            if not isinstance(price,(int,float)) or price < 0 or price > 999999:
                raise HTTPException(status_code=400,detail="价格不合法")
        return OrderDAO.update_order(db,order_id,update_data)