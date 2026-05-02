"""
订单模块 业务逻辑层
===================
和商品模块最大的区别: 【数据权限】

每个用户只能看到和操作自己的订单.

【校验链】每个操作都必须过3关:
  1. 数据存在性 (订单存在吗?)
  2. 用户归属权 (是你的订单吗?)
  3. 业务合法性 (状态允许修改吗?)
"""
from dao.order_dao import OrderDAO
from sqlalchemy.orm import Session
from schema.order_schema import OrderCreate, OrderUpdate
from model.order_info import Order
from core.logger import log_action
from core.exception import ValidationException,BusinessException,NotFoundException,ForbiddenException



DEFAULT_PENDING_STATUS = "待支付"
VALID_STATUS = ["待支付", "已支付", "已取消"]


class OrderService:
    """
    订单业务逻辑处理器
    """

    # ======================================================================
    # 基础 CRUD 方法
    # ======================================================================

    @staticmethod
    @log_action("创建订单")
    def create_order(
        db: Session,
        order_create: OrderCreate,
        current_user_id: int
    ) -> Order:
        """
        创建订单, 完整的校验链
        
        【关键设计: user_id自动绑定】
          【绝对不要】相信前端传的user_id!
          【永远】从认证的token里提取!
          防止用户给别人创建假订单
        """
        data = order_create.model_dump()
        
        total_price = data.get("total_price", 0)
        if not isinstance(total_price, int) or total_price < 0 or total_price > 999999:
            raise ValidationException("价格必须在0~999999之间")
        
        order_no = str(data.get("order_no", "")).strip()
        if not order_no or len(order_no) > 50:
            raise ValidationException("订单编号必须在1~50个字符之间")
        
        exists = OrderDAO.query_by_order_no(db, order_no)
        if exists:
            raise BusinessException("订单编号已存在")
        
        status = data.get("status", DEFAULT_PENDING_STATUS)
        if status not in VALID_STATUS:
            raise ValidationException(f"订单状态必须是: {VALID_STATUS}")
        
        data["user_id"] = current_user_id
        
        return OrderDAO.create_order(db, OrderCreate(**data))

    @staticmethod
    @log_action("查询订单")
    def query_order(db: Session, order_id: int, current_user_id: int) -> Order:
        """
        查询单个订单
        
        2次校验:
          1. 订单是否存在
          2. 是否属于当前用户
        """
        order = OrderDAO.query_order(db, order_id)
        if not order:
            raise NotFoundException("订单不存在")
        
        if order.user_id != current_user_id:
            raise ForbiddenException("无权限查看该订单")
        
        return order

    @staticmethod
    @log_action("查询订单列表")
    def query_list(
        db: Session,
        page: None | str | int,
        size: None | str | int,
        current_user_id: int
    ) -> dict:
        """
        分页查询当前用户的订单列表
        
        【关键】自动过滤user_id
               不用前端传, 永远不会拿到别人的订单
        """
        try:
            page = int(page) if page not in (None, "") else 1
            size = int(size) if size not in (None, "") else 10
            
            page = max(page, 1)
            size = min(size, 100)
            
            return OrderDAO.list_order(
                db,
                page=page,
                size=size,
                user_id=current_user_id
            )
        except Exception:
            return {
                "list": [],
                "page": 1,
                "size": 10,
                "total": 0,
                "total_pages": 0
            }

    @staticmethod
    @log_action("更新订单")
    def update_order(db: Session, order_id: int, order_update: OrderUpdate, current_user_id: int) -> Order:
        """
        更新订单信息
        
        校验链: 存在 → 归属 → 状态合法
        """
        order = OrderService.query_order(db, order_id, current_user_id)
        update_data = order_update.model_dump(exclude_unset=True)
        
        if "total_price" in update_data:
            price = update_data["total_price"]
            if not isinstance(price, int) or price < 0 or price > 999999:
                raise ValidationException("价格必须在0~999999之间")
        
        if "status" in update_data:
            if update_data["status"] not in VALID_STATUS:
                raise ValidationException(f"订单状态必须是: {VALID_STATUS}")
        
        return OrderDAO.update_order(db, order_id, update_data)

    @staticmethod
    @log_action("删除订单")
    def delete_order(db: Session, order_id: int, current_user_id: int) -> bool:
        """
        软删除订单
        
        校验链: 存在性 → 归属权
        """
        OrderService.query_order(db, order_id, current_user_id)
        return OrderDAO.delete_order(db, order_id)

    # ======================================================================
    # 回收站相关方法
    # ======================================================================

    @staticmethod
    @log_action("查询回收站订单列表")
    def deleted_list(
        db: Session,
        page: None | str | int,
        size: None | str | int,
        current_user_id: int
    ) -> dict:
        """
        查询当前用户的回收站订单列表
        """
        try:
            page = int(page) if page not in (None, "") else 1
            size = int(size) if size not in (None, "") else 10
            
            page = max(page, 1)
            size = min(size, 100)
            
            return OrderDAO.deleted_list(
                db,
                page=page,
                size=size,
                user_id=current_user_id
            )
        except Exception:
            return {
                "list": [],
                "page": 1,
                "size": 10,
                "total": 0,
                "total_pages": 0
            }

    @staticmethod
    @log_action("恢复订单")
    def restore_order(db: Session, order_id: int, current_user_id: int) -> bool:
        """
        从回收站恢复订单
        """
        order = OrderDAO.query_deleted_order(db, order_id)
        if not order:
            raise NotFoundException("回收站中不存在该订单")
        
        if order.user_id != current_user_id:
            raise ForbiddenException("无权限恢复该订单")
        
        return OrderDAO.restore_order(db, order_id)

    @staticmethod
    @log_action("永久删除订单")
    def hard_delete_order(db: Session, order_id: int, current_user_id: int) -> bool:
        """
        永久删除订单 (不可逆!)
        
        安全机制: 只能删除【已经在回收站】的订单
        """
        order = OrderDAO.query_deleted_order(db, order_id)
        if not order:
            raise BusinessException("只能永久删除回收站中的订单")
        
        if order.user_id != current_user_id:
            raise ForbiddenException("无权限删除该订单")
        
        return OrderDAO.hard_delete_order(db, order_id)
