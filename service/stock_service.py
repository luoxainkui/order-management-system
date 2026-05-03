"""
库存模块 业务逻辑层
==================
防御式编程完整校验链

【核心设计】: 校验执行顺序 - 从快到慢
  1. 非空校验 (内存操作, 最快)
  2. 范围/格式校验 (内存操作)
  3. 存在性/唯一性校验 (查数据库, 最慢)
"""
from dao.stock_dao import StockDAO
from dao.product_dao import ProductDAO
from sqlalchemy.orm import Session
from schema.stock_schema import StockCreate, StockUpdate
from model.stock import Stock
from core.logger import log_action
from core.exception import ValidationException, BusinessException, NotFoundException


class StockService:
    """
    库存业务逻辑静态类

    所有方法都是无状态的, 接收 db 作为第一个参数
    """

    # ======================================================================
    # 基础 CRUD 方法
    # ======================================================================

    @staticmethod
    @log_action("创建库存")
    def create_stock(db: Session, stock_create: StockCreate) -> Stock:
        """
        创建库存记录

        核心校验:
          1. 关联商品必须存在
          2. 同一商品不能重复创建库存
        """
        product = ProductDAO.query_product(db, stock_create.product_id)
        if not product:
            raise NotFoundException("关联的商品不存在")

        existing = StockDAO.query_by_product_id(db, stock_create.product_id)
        if existing:
            raise BusinessException("该商品已有关联库存记录，请使用更新接口")

        if stock_create.quantity < 0:
            raise ValidationException("库存数量不能小于0")

        if stock_create.locked_quantity < 0:
            raise ValidationException("锁定库存数量不能小于0")

        data = stock_create.model_dump()
        return StockDAO.create_stock(db, data)

    @staticmethod
    @log_action("查询库存")
    def query_stock(db: Session, stock_id: int) -> Stock:
        """
        查询单个库存记录
        """
        stock = StockDAO.query_stock(db, stock_id)
        if not stock:
            raise NotFoundException("库存记录不存在")
        return stock

    @staticmethod
    @log_action("查询库存列表")
    def query_list(
        db: Session,
        page: None | str | int,
        size: None | str | int
    ) -> dict:
        """
        分页查询库存列表, 带参数容错
        """
        try:
            page = int(page) if page not in (None, "") else 1
            size = int(size) if size not in (None, "") else 10

            page = max(page, 1)
            size = min(size, 100)

            return StockDAO.list_stock(db, page=page, size=size)
        except Exception:
            return {
                "list": [],
                "page": 1,
                "size": 10,
                "total": 0,
                "total_pages": 0
            }

    @staticmethod
    @log_action("更新库存")
    def update_stock(
        db: Session,
        stock_id: int,
        stock_update: StockUpdate
    ) -> Stock:
        """
        更新库存信息

        校验链: 存在性 → 参数合法性
        """
        StockService.query_stock(db, stock_id)
        update_data = stock_update.model_dump(exclude_unset=True)

        if "quantity" in update_data and update_data["quantity"] < 0:
            raise ValidationException("库存数量不能小于0")

        if "locked_quantity" in update_data and update_data["locked_quantity"] < 0:
            raise ValidationException("锁定库存数量不能小于0")

        return StockDAO.update_stock(db, stock_id, update_data)

    @staticmethod
    @log_action("删除库存")
    def delete_stock(db: Session, stock_id: int) -> bool:
        """
        软删除库存记录
        """
        StockService.query_stock(db, stock_id)
        return StockDAO.delete_stock(db, stock_id)

    # ======================================================================
    # 回收站相关方法
    # ======================================================================

    @staticmethod
    @log_action("查询回收站库存列表")
    def deleted_list(
        db: Session,
        page: None | str | int,
        size: None | str | int
    ) -> dict:
        """
        查询回收站库存列表
        """
        try:
            page = int(page) if page not in (None, "") else 1
            size = int(size) if size not in (None, "") else 10

            page = max(page, 1)
            size = min(size, 100)

            return StockDAO.deleted_list(db, page=page, size=size)
        except Exception:
            return {
                "list": [],
                "page": 1,
                "size": 10,
                "total": 0,
                "total_pages": 0
            }

    @staticmethod
    @log_action("恢复库存")
    def restore_stock(db: Session, stock_id: int) -> bool:
        """
        从回收站恢复库存记录
        """
        stock = StockDAO.query_deleted_stock(db, stock_id)
        if not stock:
            raise NotFoundException("回收站中不存在该库存记录")

        return StockDAO.restore_stock(db, stock_id)

    @staticmethod
    @log_action("永久删除库存")
    def hard_delete_stock(db: Session, stock_id: int) -> bool:
        """
        永久删除库存记录 (不可逆!)

        安全机制: 只能删除【已经在回收站】的库存
        """
        stock = StockDAO.query_deleted_stock(db, stock_id)
        if not stock:
            raise BusinessException("只能永久删除回收站中的库存记录")

        return StockDAO.hard_delete_stock(db, stock_id)