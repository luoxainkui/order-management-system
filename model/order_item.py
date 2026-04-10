#    订单明细表
# 导入数据库基建，继承表
from core.db import Base
# 导入时间
from datetime import datetime 
# 导入字段类型：列、整数、字符串
from sqlalchemy import Column,Integer,DateTime,String

class OrderItem(Base):
    __tablename__ = "orderitem"
    # 主键：自增ID，用于唯一标识，加速查询，非空
    id = Column(Integer,primary_key=True,index=True)
    # 所属订单id，整数，非空
    order_id = Column(Integer,nullable=False)
    # 购买商品id，整数，非空
    product_id = Column(Integer,nullable=False)
    # 商品名称，整数，非空
    product_name = Column(String(100),nullable=False)
    # 商品单价，整数非空
    price = Column(Integer,nullable=False)
    # 购买数量，整数，非空
    count = Column(Integer,nullable=False)
    # 获取时间：存入数据库，请求系统时间now
    created_at = Column(DateTime, default=datetime.now)