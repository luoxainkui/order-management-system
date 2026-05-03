"""
用户模块 DAO 数据访问层
======================
SQLAlchemy ORM 原生查询

设计原则: SQL,不做任何业务判断!
"""
from sqlalchemy.orm import Session
from model.user import User
from datetime import datetime
from schema.user_schema import UserCreate


class UserDAO:
    """
    用户数据库操作静态类
    """

    # ======================================================================
    # 基础 CRUD 操作
    # ======================================================================

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        db_user = User(**user_create.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def query_user(db: Session, user_id: int, *, include_deleted: bool = False) -> User | None:
        query = db.query(User).filter(User.id == user_id)
        if not include_deleted:
            query = query.filter(User.is_delete == 0)
        return query.first()

    @staticmethod
    def query_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(
            User.username == username,
            User.is_delete == 0
        ).first()

    @staticmethod
    def query_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(
            User.email == email,
            User.is_delete == 0
        ).first()

    @staticmethod
    def list_user(db: Session, page: int, size: int) -> dict:
        query = db.query(User).filter(User.is_delete == 0)

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
    def update_user(db: Session, user_id: int, update_data: dict) -> User:
        db.query(User).filter(User.id == user_id).update(update_data)
        db.commit()
        return UserDAO.query_user(db, user_id)

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        update_data = {"is_delete": 1, "delete_time": datetime.now()}
        db.query(User).filter(User.id == user_id).update(update_data)
        db.commit()
        return True

    # ======================================================================
    # 回收站相关操作
    # ======================================================================

    @staticmethod
    def query_deleted_user(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(
            User.id == user_id,
            User.is_delete == 1
        ).first()

    @staticmethod
    def deleted_list(db: Session, page: int, size: int) -> dict:
        query = db.query(User).filter(User.is_delete == 1)

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
    def restore_user(db: Session, user_id: int) -> bool:
        update_data = {"is_delete": 0, "delete_time": None}
        db.query(User).filter(User.id == user_id).update(update_data)
        db.commit()
        return True

    @staticmethod
    def hard_delete_user(db: Session, user_id: int) -> bool:
        db.query(User).filter(User.id == user_id).delete()
        db.commit()
        return True