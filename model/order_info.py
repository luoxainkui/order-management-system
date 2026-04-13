#       订单表
# 数据库保存
from core.db import Base
# 时间
from datetime import datetime
# 订单信息
from sqlalchemy import Column,Integer,String,DateTime,Boolean


class Order(Base):
    __tablename__ = "order"
    # 主键：自增ID，用于唯一标识，加速查询，非空
    id = Column(Integer,primary_key=True,index=True)
    # 订单编号：50字符，唯一，非空
    order_no = Column(String(50), unique=True, nullable=False)
    # 下单用户ID
    user_id = Column(Integer,nullable=False)
    # 订单总价格
    total_price = Column(Integer,nullable=False)
    # 订单总状态，默认待支付
    status = Column(String(20), default="待支付")
    # 获取时间：存入数据库，请求系统时间now
    created_at = Column(DateTime, default=datetime.now)


# 软删除类型
    # 判断删除False/True
    is_delete = Column(Boolean,default=False)
    # 添加时间默认空值
    delete_time = Column(DateTime,nullable=True)