"""
订单模块 DAO 数据访问层
======================
SQLAlchemy ORM 原生查询

和商品DAO的区别: 几乎所有查询都要带user_id过滤.
这就是数据权限的底层实现.
"""
from model.order_info import Order
from sqlalchemy.orm import Session
from datetime import datetime
from schema.order_schema import OrderCreate


class OrderDAO:
    """
    订单数据库操作静态类
    """

    # ======================================================================
    # 基础 CRUD 操作
    # ======================================================================

    @staticmethod
    def create_order(db: Session, order_create: OrderCreate) -> Order:
        db_order = Order(**order_create.model_dump())
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def query_order(
        db: Session,
        order_id: int,
        *,
        include_deleted: bool = False,
        only_deleted: bool = False
    ) -> Order | None:
        query = db.query(Order).filter(Order.id == order_id)
        if only_deleted:
            query = query.filter(Order.is_delete == 1)
        elif not include_deleted:
            query = query.filter(Order.is_delete == 0)
        return query.first()

    @staticmethod
    def query_by_order_no(db: Session, order_no: str) -> Order | None:
        return db.query(Order).filter(
            Order.order_no == order_no,
            Order.is_delete == 0
        ).first()

    @staticmethod
    def list_order(db: Session, page: int, size: int, user_id: int) -> dict:
        query = db.query(Order).filter(Order.is_delete == 0, Order.user_id == user_id)
        
        total = query.count()
        total_pages = (total + size - 1) // size
        items = query.offset((page - 1) * size).limit(size).all()
        
        return {
            "list": items,
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages
        }

    @staticmethod
    def update_order(db: Session, order_id: int, update_data: dict) -> Order:
        db.query(Order).filter(Order.id == order_id).update(update_data)
        db.commit()
        return OrderDAO.query_order(db, order_id)

    @staticmethod
    def delete_order(db: Session, order_id: int) -> bool:
        update_data = {"is_delete": 1, "delete_time": datetime.now()}
        db.query(Order).filter(Order.id == order_id).update(update_data)
        db.commit()
        return True

    # ======================================================================
    # 回收站相关操作
    # ======================================================================

    @staticmethod
    def query_deleted_order(db: Session, order_id: int) -> Order | None:
        return db.query(Order).filter(
            Order.id == order_id,
            Order.is_delete == 1
        ).first()

    @staticmethod
    def deleted_list(db: Session, page: int, size: int, user_id: int) -> dict:
        query = db.query(Order).filter(Order.is_delete == 1, Order.user_id == user_id)
        
        total = query.count()
        total_pages = (total + size - 1) // size
        items = query.offset((page - 1) * size).limit(size).all()
        
        return {
            "list": items,
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages
        }

    @staticmethod
    def restore_order(db: Session, order_id: int) -> bool:
        update_data = {"is_delete": 0, "delete_time": None}
        db.query(Order).filter(Order.id == order_id).update(update_data)
        db.commit()
        return True

    @staticmethod
    def hard_delete_order(db: Session, order_id: int) -> bool:
        db.query(Order).filter(Order.id == order_id).delete()
        db.commit()
        return True
