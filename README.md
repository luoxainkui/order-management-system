# 订单管理系统

基于 FastAPI + SQLAlchemy 的分层架构订单管理系统。

## 技术栈
- FastAPI 接口框架
- SQLAlchemy ORM
- 统一响应格式
- 全局异常降级处理器
- AOP 日志埋点
- 软删除/回收站机制

## 架构设计
```
API层        →  路由分发，参数接收
Service层    →  业务逻辑，参数校验
DAO层        →  数据库操作，原子性
Model层      →  数据库映射
Schema层     →  请求/响应参数校验
```

## 运行方式
```bash
uvicorn main:app --reload
```

## 接口文档
- Swagger UI: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 已实现模块
- ✅ 商品管理模块
- ✅ 订单管理模块
- ✅ 用户登录注册模块
