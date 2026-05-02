"""
商品模块 数据库Model
====================
一行一个字段
"""
from core.db import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime


class Product(Base):
    """商品表"""
    __tablename__ = "product"

    id          = Column(Integer, primary_key=True, index=True, comment="主键ID")
    product_no  = Column(String(50), unique=True, index=True, nullable=False, comment="商品编号")
    name        = Column(String(100), nullable=False, comment="商品名称")
    price       = Column(Integer, nullable=False, comment="商品价格(分)")
    stock       = Column(Integer, default=0, comment="库存数量")
    
    is_delete   = Column(Integer, default=0, comment="软删除标记")
    created_at  = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at  = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    delete_time = Column(DateTime, comment="删除时间")
