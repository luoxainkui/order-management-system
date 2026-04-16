# 订单服务层，实现业务逻辑和校验规则
from dao.order_dao import OrderDAO
from sqlalchemy.orm import Session
from schema.order_schema import OrderCreate,OrderUpdate
from model.order_info import Order
from fastapi import HTTPException
from core.logger import log_action

class OrderService:
    """
    业务逻辑层
    """
    @staticmethod
    def query_order(db:Session,order_id:int,current_user_id:int) ->None|Order:
        """
        根据订单ID查询订单,并校验当前用户是否有权限访问。

        :param db: 数据库会话
        :param order_id: 订单ID
        :param current_user_id: 当前登录用户ID
        :return: 订单对象，或抛出 HTTPException
        """
        order = OrderDAO.query_order(db,order_id)
        if not order:
            raise HTTPException(status_code=404,detail="订单不存在")
        if order.user_id!=current_user_id:
            raise HTTPException(status_code=403,detail="你无权限查看此订单")
        return order

    @staticmethod
    def query_list(db:Session,page: None, size: None, current_user_id: int | None = None) ->Order|dict:
        """
        分页查询订单列表，用于页面展示。

        :param db: 数据库会话
        :param page: 页码(异常或空值时默认1)
        :param size: 每页条数(异常或空值时默认10)
        :param current_user_id: 可选的当前用户ID过滤
        :return: 包含分页信息的字典
        """
        try:
            page = int(page) if page not in (None,"") else 1
            size = int(size) if size not in (None,"") else 10

            page = max(page,1)
            size = min(size,100)

            return OrderDAO.list_order(db,page=page,size=size,user_id=current_user_id)
        except Exception:
            return {"list" : [],"page" : 1,"size" : 10,"total" : 0,"total_pages" : 0}

    @staticmethod
    def deleted_list(db:Session,page: None,size: None, current_user_id: int | None = None) ->Order|dict:
        """
        分页查询已软删除订单，用于回收站页面展示。

        :param db: 数据库会话
        :param page: 页码(异常或空值时默认1)
        :param size: 每页条数(异常或空值时默认10)
        :param current_user_id: 可选的当前用户ID过滤
        :return: 包含回收站分页数据的字典
        """
        try:
            page = int(page) if page not in (None,"") else 1
            size = int(size) if size not in (None,"") else 10

            page = max(page,1)
            size = min(size,10)
            
            return OrderDAO.deleted_list(db,page=page,size=size,user_id=current_user_id)
        except Exception:
            return {"list" : [],"page" : 1,"size" : 10,"total" : 0,"total_pages" : 0}

    @staticmethod
    @log_action('创建订单')
    def create_order(db:Session,order_create:OrderCreate,current_user_id:int) ->Order|None:
        """
        创建订单并执行必要校验：价格、订单号、用户权限和查重。

        :param db: 数据库会话
        :param order_create: 前端传入的订单数据
        :param current_user_id: 当前登录用户ID
        :return: 创建成功的订单对象
        :raises HTTPException: 价格、订单号不合法或订单已存在
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
    @log_action('修改订单')
    def update_order(db:Session,order_id:int,update_data:OrderUpdate,current_user_id:int)->Order:
        """
        修改订单信息，并校验用户权限、价格范围和订单编号唯一性。

        :param db: 数据库会话
        :param order_id: 要修改的订单ID
        :param update_data: 前端传入的更新字段
        :param current_user_id: 当前登录用户ID
        :return: 更新后的订单对象
        :raises HTTPException: 权限不足、订单不存在、参数不合法
        """
        order = OrderDAO.query_order(db,order_id)
        if not order:
            raise HTTPException(status_code=404,detail="订单不存在")
        if order.user_id != current_user_id:
            raise HTTPException(status_code=403,detail="无权修改此订单")
        
        update_fields = update_data.model_dump(exclude_unset=True, exclude={"user_id"})
        if not update_fields:
            raise HTTPException(status_code=400,detail="没有可更新的字段")

        if "total_price" in update_fields:
            price = update_fields["total_price"]
            if not isinstance(price,(int,float)) or price < 0 or price > 999999:
                raise HTTPException(status_code=400,detail="价格不合法")

        if "order_no" in update_fields:
            order_no = str(update_fields["order_no"]).strip()
            if not order_no or len(order_no) > 50:
                raise HTTPException(status_code=400,detail="订单编号不合法")
            exists = OrderDAO.query_by_order_no(db,order_no)
            if exists and exists.id != order_id:
                raise HTTPException(status_code=400,detail="订单编号已经重复")
        return OrderDAO.update_order(db,order_id,update_data)

    @staticmethod
    @log_action('软删除订单')
    def delete_order(db:Session,order_id:int,current_user_id:int) -> bool:
        """
        软删除订单，设置删除标记并记录删除时间。

        :param db: 数据库会话
        :param order_id: 要软删除的订单ID
        :param current_user_id: 当前登录用户ID
        :return: 删除成功返回 True
        :raises HTTPException: 订单不存在或无权限删除
        """
        order = OrderDAO.query_order(db,order_id)
        if not order:
            raise HTTPException(status_code=404,detail="订单不存在")
        if order.user_id != current_user_id:
            raise HTTPException(status_code=403,detail="无权删除此订单")

        success = OrderDAO.delete_order(db,order_id)
        if not success:
            raise HTTPException(status_code=400,detail="删除失败")
        return True

    @staticmethod
    @log_action('恢复订单')
    def restore_order(db:Session,order_id:int,current_user_id:int) -> bool:
        """
        恢复已软删除订单，取消删除标记。

        :param db: 数据库会话
        :param order_id: 要恢复的订单ID
        :param current_user_id: 当前登录用户ID
        :return: 恢复成功返回 True
        :raises HTTPException: 订单不存在、未删除或无权限恢复
        """
        order = OrderDAO.query_order(db, order_id, only_deleted=True)
        if not order:
            raise HTTPException(status_code=404,detail="订单不存在或未删除")
        if order.user_id != current_user_id:
            raise HTTPException(status_code=403,detail="无权恢复此订单")

        success = OrderDAO.restore_order(db,order_id)
        if not success:
            raise HTTPException(status_code=400,detail="恢复失败")
        return True

    @staticmethod
    @log_action('永久删除订单')
    def hard_delete_order(db:Session,order_id:int,current_user_id:int) -> bool:
        """
        永久删除订单记录，彻底从数据库中移除。

        :param db: 数据库会话
        :param order_id: 要永久删除的订单ID
        :param current_user_id: 当前登录用户ID
        :return: 删除成功返回 True
        :raises HTTPException: 订单不存在或无权限永久删除
        """
        order = OrderDAO.query_order(db, order_id, include_deleted=True)
        if not order:
            raise HTTPException(status_code=404,detail="订单不存在")
        if order.user_id != current_user_id:
            raise HTTPException(status_code=403,detail="无权永久删除此订单")

        success = OrderDAO.hard_order(db,order_id)
        if not success:
            raise HTTPException(status_code=400,detail="永久删除失败")
        return True