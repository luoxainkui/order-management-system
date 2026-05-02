"""
库存模块 数据库Model
====================
一行一个字段
"""
from core.db import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime


class Stock(Base):
    """库存表"""
    __tablename__ = "stock"

    id              = Column(Integer, primary_key=True, index=True, comment="主键ID")
    product_id      = Column(Integer, index=True, nullable=False, comment="关联商品ID")
    warehouse       = Column(String(50), comment="仓库名称")
    quantity        = Column(Integer, default=0, comment="库存数量")
    locked_quantity = Column(Integer, default=0, comment="锁定库存数量")
    
    is_delete       = Column(Integer, default=0, comment="软删除标记")
    created_at      = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at      = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    delete_time     = Column(DateTime, comment="删除时间")
