"""
商品模块 DAO 数据访问层
======================
SQLAlchemy ORM 原生查询

设计原则: SQL,不做任何业务判断!
"""
from model.product import Product
from sqlalchemy.orm import Session
from datetime import datetime
from schema.product_schema import ProductCreate


class ProductDAO:
    """
    商品数据库操作静态类
    """

    # ======================================================================
    # 基础 CRUD 操作
    # ======================================================================

    @staticmethod
    def create_product(db: Session, product_create: ProductCreate) -> Product:
        db_product = Product(**product_create.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def query_product(db: Session, product_id: int, *, include_deleted: bool = False) -> Product | None:
        query = db.query(Product).filter(Product.id == product_id)
        if not include_deleted:
            query = query.filter(Product.is_delete == 0)
        return query.first()

    @staticmethod
    def query_no_product(db: Session, product_no: str) -> Product | None:
        return db.query(Product).filter(
            Product.product_no == product_no,
            Product.is_delete == 0
        ).first()

    @staticmethod
    def query_name_product(db: Session, name: str) -> Product | None:
        return db.query(Product).filter(
            Product.name == name,
            Product.is_delete == 0
        ).first()

    @staticmethod
    def list_product(db: Session, page: int, size: int, name: str | None = None) -> dict:
        query = db.query(Product).filter(Product.is_delete == 0)
        if name:
            query = query.filter(Product.name.contains(name))
        
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
    def update_product(db: Session, product_id: int, update_data: dict) -> Product:
        db.query(Product).filter(Product.id == product_id).update(update_data)
        db.commit()
        return ProductDAO.query_product(db, product_id)

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        update_data = {"is_delete": 1, "delete_time": datetime.now()}
        db.query(Product).filter(Product.id == product_id).update(update_data)
        db.commit()
        return True

    # ======================================================================
    # 回收站相关操作
    # ======================================================================

    @staticmethod
    def query_deleted_product(db: Session, product_id: int) -> Product | None:
        return db.query(Product).filter(
            Product.id == product_id,
            Product.is_delete == 1
        ).first()

    @staticmethod
    def deleted_list(db: Session, page: int, size: int, name: str | None = None) -> dict:
        query = db.query(Product).filter(Product.is_delete == 1)
        if name:
            query = query.filter(Product.name.contains(name))
        
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
    def restore_product(db: Session, product_id: int) -> bool:
        update_data = {"is_delete": 0, "delete_time": None}
        db.query(Product).filter(Product.id == product_id).update(update_data)
        db.commit()
        return True

    @staticmethod
    def hard_delete_product(db: Session, product_id: int) -> bool:
        db.query(Product).filter(Product.id == product_id).delete()
        db.commit()
        return True
