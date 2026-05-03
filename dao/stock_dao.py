"""
库存模块 DAO 数据访问层
======================
SQLAlchemy ORM 原生查询

设计原则: 只写 SQL, 不做任何业务判断!
"""
from sqlalchemy.orm import Session
from model.stock import Stock
from datetime import datetime


class StockDAO:
    """
    库存数据库操作静态类
    """

    # ======================================================================
    # 基础 CRUD 操作
    # ======================================================================

    @staticmethod
    def create_stock(db: Session, data: dict) -> Stock:
        db_stock = Stock(**data)
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
        return db_stock

    @staticmethod
    def query_stock(db: Session, stock_id: int, *, include_deleted: bool = False) -> Stock | None:
        query = db.query(Stock).filter(Stock.id == stock_id)
        if not include_deleted:
            query = query.filter(Stock.is_delete == 0)
        return query.first()

    @staticmethod
    def query_by_product_id(db: Session, product_id: int) -> Stock | None:
        return db.query(Stock).filter(
            Stock.product_id == product_id,
            Stock.is_delete == 0
        ).first()

    @staticmethod
    def list_stock(db: Session, page: int, size: int) -> dict:
        query = db.query(Stock).filter(Stock.is_delete == 0)

        total = query.count()
        total_pages = (total + size - 1) // size if size > 0 else 0
        items = query.offset((page - 1) * size).limit(size).all()

        return {
            "list": items,
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages
        }

    @staticmethod
    def update_stock(db: Session, stock_id: int, update_data: dict) -> Stock:
        db.query(Stock).filter(Stock.id == stock_id).update(update_data)
        db.commit()
        return StockDAO.query_stock(db, stock_id)

    @staticmethod
    def delete_stock(db: Session, stock_id: int) -> bool:
        update_data = {"is_delete": 1, "delete_time": datetime.now()}
        db.query(Stock).filter(Stock.id == stock_id).update(update_data)
        db.commit()
        return True

    # ======================================================================
    # 回收站相关操作
    # ======================================================================

    @staticmethod
    def query_deleted_stock(db: Session, stock_id: int) -> Stock | None:
        return db.query(Stock).filter(
            Stock.id == stock_id,
            Stock.is_delete == 1
        ).first()

    @staticmethod
    def deleted_list(db: Session, page: int, size: int) -> dict:
        query = db.query(Stock).filter(Stock.is_delete == 1)

        total = query.count()
        total_pages = (total + size - 1) // size if size > 0 else 0
        items = query.offset((page - 1) * size).limit(size).all()

        return {
            "list": items,
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages
        }

    @staticmethod
    def restore_stock(db: Session, stock_id: int) -> bool:
        update_data = {"is_delete": 0, "delete_time": None}
        db.query(Stock).filter(Stock.id == stock_id).update(update_data)
        db.commit()
        return True

    @staticmethod
    def hard_delete_stock(db: Session, stock_id: int) -> bool:
        db.query(Stock).filter(Stock.id == stock_id).delete()
        db.commit()
        return True