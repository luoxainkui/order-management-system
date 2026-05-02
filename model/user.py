"""
用户模块 数据库Model
====================
一行一个字段
"""
from core.db import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime


class User(Base):
    """用户表"""
    __tablename__ = "user"

    id          = Column(Integer, primary_key=True, index=True, comment="主键ID")
    username    = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password    = Column(String(255), nullable=False, comment="加密密码")
    phone       = Column(String(20), comment="手机号")
    email       = Column(String(100), comment="邮箱")
    
    is_delete   = Column(Integer, default=0, comment="软删除标记")
    created_at  = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at  = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    delete_time = Column(DateTime, comment="删除时间")
