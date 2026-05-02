"""
订单模块 数据库Model
====================
一行一个字段
"""
from core.db import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime


class Order(Base):
    """订单表"""
    __tablename__ = "order_info"

    id          = Column(Integer, primary_key=True, index=True, comment="主键ID")
    user_id     = Column(Integer, index=True, nullable=False, comment="用户ID")
    order_no    = Column(String(50), unique=True, index=True, nullable=False, comment="订单编号")
    total_price = Column(Integer, nullable=False, comment="订单总金额(分)")
    status      = Column(String(20), default="待支付", comment="订单状态")
    
    is_delete   = Column(Integer, default=0, comment="软删除标记")
    created_at  = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at  = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    delete_time = Column(DateTime, comment="删除时间")
