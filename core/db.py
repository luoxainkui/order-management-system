"""
数据库核心模块
=============
SQLAlchemy 核心配置，工业级数据库连接方案
这是整个系统数据层的基石,所有Model/DAO都依赖这里

设计要点：
  1. 连接池自动管理，不需要手动开关
  2. 断线自动重连（工业级必备）
  3. 依赖注入式Session管理
  4. 自动建表ORM支持
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import settings


# ===================== 数据库连接URL构建 =====================
# 为什么用utf8mb4而不是utf8？
# utf8mb4支持emoji表情和所有生僻汉字，真正的UTF-8，工业级标准
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    f"?charset=utf8mb4&collation=utf8mb4_unicode_ci"
)


# ===================== 数据库引擎（单例） =====================
# create_engine 是整个SQLAlchemy的核心，全局只创建一次
# 千万不要在循环里调用create_engine！
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,   # 【工业级必备】每次取连接前ping一下，死连接自动重建
                          # 解决MySQL默认8小时断线问题，不加这个线上必出诡异bug
    echo=False            # SQL日志开关，开发时可改成True看执行的SQL
)


# ===================== Session工厂 =====================
# Session = 数据库会话，相当于一次数据库连接
# SessionLocal是工厂函数，调用它才产生真实的会话
# 重要：每个请求用一个独立的Session，用完关闭
SessionLocal = sessionmaker(
    autocommit=False,     # 禁止自动提交，事务由代码控制
    autoflush=False,      # 禁止自动刷写，手动commit才执行
    bind=engine
)


# ===================== ORM基类 =====================
# 所有的数据库Model必须继承这个Base
# SQLAlchemy会自动扫描所有子类建表
Base = declarative_base()


# ===================== 全局依赖注入 =====================
"""
FastAPI 依赖注入标准写法，所有接口这么用：
def xxx_api(db: Session = Depends(get_db))

设计精妙之处：
  1. 进入接口时自动创建新的Session
  2. try...finally 保证无论接口是否报错,Session一定关闭
  3. yield是Python生成器语法,实现了"进入时执行，退出时清理"的AOP切面

反模式：千万不要在函数里手动 SessionLocal()！那样会连接泄漏！
"""
def get_db():
    db = SessionLocal()  # 进入接口：创建一个全新的数据库会话
    try:
        yield db         # 把会话交给接口函数使用
    finally:
        db.close()       # 无论接口成功/失败，一定会关闭连接（防泄漏）
