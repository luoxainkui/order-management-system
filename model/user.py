#     用户信息导入
# 导入数据库基建，继承表
from core.db import Base
# 导入字段类型：列、整数、字符串
from sqlalchemy import Column,Integer,String,DateTime 
# 导入时间
from datetime import datetime 


class User(Base):
    # 命名
    __tablename__ = "user"
    # 主键：自增ID，用于唯一标识，加速查询，非空
    id = Column(Integer,primary_key=True,index=True)
    # 用户名：最大50字符、唯一不重复、非空，用于用户登录标识
    username = Column(String(50),unique=True,nullable=False)
    # 密码：最大100字符，非空，储存加密后密码
    password = Column(String(100),nullable=False)
    #获取时间：存入数据库，请求系统时间now
    created_at = Column(DateTime, default=datetime.now)