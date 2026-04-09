#      商品表
# 导入数据库基建，继承表
from core.db import Base
# 导入时间
from datetime import datetime
# 导入字段类型：列、整数、字符串
from sqlalchemy import Column,Integer,String,DateTime


class Product(Base):
    __tablename__ = "product"
    # 主键：自增ID，用于唯一标识，加速查询，非空
    id = Column(Integer,primary_key=True,index=True)
    # 商品名称，100字符，非空
    name = Column(String(100),nullable=False)
    # 商品价格，整数，非空
    price = Column(Integer,nullable=False)
    # 商品数量，整数，默认0
    stock = Column(Integer,default=0)
    # 获取时间：存入数据库，请求系统时间now
    created_at = Column(DateTime, default=datetime.now)
    