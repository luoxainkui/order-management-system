# 订单管理系统

基于 **FastAPI + SQLAlchemy** 的分层架构订单管理系统，践行工业级四层分离设计。

---

## 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| Web框架 | FastAPI 0.135 | 高性能异步API框架，自动生成Swagger文档 |
| ORM | SQLAlchemy 2.0 | 数据库ORM，连接池 + 断线重连 |
| 校验 | Pydantic 2.12 | 请求参数自动校验 |
| 认证 | passlib + bcrypt | 密码哈希加密 |
| 数据库 | MySQL (PyMySQL) | 关系型数据库 |
| 服务器 | Uvicorn | ASGI服务器，热重载开发 |

---

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│  API 层      路由分发，参数接收，调用Service             │
│  (api/)      反模式：不要在API层写业务逻辑！             │
├─────────────────────────────────────────────────────────┤
│  Schema 层   请求/响应参数校验 (Pydantic)                 │
│  (schema/)   由快到慢：非空 → 格式 → 长度范围            │
├─────────────────────────────────────────────────────────┤
│  Service 层   业务逻辑，参数校验，防腐层                   │
│  (service/)  校验链：内存校验 → 数据库校验                │
├─────────────────────────────────────────────────────────┤
│  DAO 层      数据库操作，纯SQL，不做业务判断              │
│  (dao/)      设计原则：只写SQL，不写if业务逻辑            │
├─────────────────────────────────────────────────────────┤
│  Model 层    数据库表映射 (SQLAlchemy ORM)               │
│  (model/)    一行一个字段，注释即文档                     │
└─────────────────────────────────────────────────────────┘
```

**数据流向**：请求 → API层(接收参数) → Schema层(格式校验) → Service层(业务校验+逻辑) → DAO层(执行SQL) → Model层(库表映射) → MySQL

---

## 数据库设计

### 商品表 `product`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 主键 |
| product_no | VARCHAR(50) UNIQUE | 商品编号 |
| name | VARCHAR(100) | 商品名称 |
| price | INT | 价格(分)，避免浮点精度问题 |
| stock | INT | 库存数量 |
| is_delete | INT | 软删除标记 (0=正常 1=已删除) |

### 订单表 `order_info`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 主键 |
| user_id | INT | 用户ID |
| order_no | VARCHAR(50) UNIQUE | 订单编号 (雪花算法生成) |
| total_price | INT | 订单总金额(分) |
| status | VARCHAR(20) | 状态：待支付/已支付/已取消 |

### 库存表 `stock`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 主键 |
| product_id | INT | 关联商品ID |
| warehouse | VARCHAR(50) | 仓库名称 |
| quantity | INT | 库存数量 |
| locked_quantity | INT | 锁定库存(防超卖) |

### 用户表 `user`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 主键 |
| username | VARCHAR(50) UNIQUE | 用户名 |
| password | VARCHAR(255) | 密码(bcrypt哈希，不可逆) |
| phone | VARCHAR(20) | 手机号 |
| email | VARCHAR(100) | 邮箱 |

> **通用字段**（所有表）：`is_delete`、`created_at`、`updated_at`、`delete_time`

---

## API 接口一览

### 商品模块 `/api/v1/products`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 分页查询商品列表 |
| GET | `/{product_id}` | 查询商品详情 |
| POST | `/create` | 创建商品 |
| PUT | `/{product_id}` | 更新商品 |
| DELETE | `/{product_id}` | 软删除商品 |
| GET | `/deleted/list` | 回收站商品列表 |
| PUT | `/restore/{product_id}` | 恢复回收站商品 |
| DELETE | `/hard/{product_id}` | 永久删除(不可逆) |

### 订单模块 `/api/v1/orders`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 分页查询订单列表 |
| GET | `/{order_id}` | 查询订单详情 |
| POST | `/create` | 创建订单 |
| PUT | `/{order_id}` | 更新订单 |
| DELETE | `/{order_id}` | 软删除订单 |
| GET | `/deleted/list` | 回收站订单列表 |
| PUT | `/restore/{order_id}` | 恢复回收站订单 |
| DELETE | `/hard/{order_id}` | 永久删除(不可逆) |

### 库存模块 `/api/v1/stocks`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 分页查询库存列表 |
| GET | `/{stock_id}` | 查询库存详情 |
| POST | `/create` | 创建库存记录 |
| PUT | `/{stock_id}` | 更新库存 |
| DELETE | `/{stock_id}` | 软删除库存 |
| GET | `/deleted/list` | 回收站库存列表 |
| PUT | `/restore/{stock_id}` | 恢复回收站库存 |
| DELETE | `/hard/{stock_id}` | 永久删除(不可逆) |

### 用户模块 `/api/v1/users`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 分页查询用户列表 |
| GET | `/{user_id}` | 查询用户详情 |
| POST | `/create` | 注册新用户 |
| PUT | `/{user_id}` | 更新用户信息 |
| DELETE | `/{user_id}` | 软删除用户 |
| GET | `/deleted/list` | 回收站用户列表 |
| PUT | `/restore/{user_id}` | 恢复回收站用户 |
| DELETE | `/hard/{user_id}` | 永久删除(不可逆) |

### 通用接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |

---

## 核心功能

### 1. 统一响应格式
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": { ... },
  "timestamp": 1714752000
}
```
所有接口返回统一JSON结构，前端无需根据接口区分处理。

### 2. 全局异常降级处理器
所有 Service 层抛出的自定义异常自动被全局处理器捕获，自动转换为标准 HTTP 响应：

| 异常类 | HTTP状态码 | 场景 |
|--------|-----------|------|
| `ValidationException` | 400 | 参数校验失败（名称为空、价格<0等） |
| `NotFoundException` | 404 | 资源不存在（查ID返回None） |
| `BusinessException` | 422 | 业务规则不允许（重复、库存不足） |
| `UnauthorizedException` | 401 | 未登录/token无效 |
| `ForbiddenException` | 403 | 无操作权限 |

**服务异常兜底**：未捕获的异常走500兜底，返回 "服务器繁忙，请稍后重试"，前端不会看到技术堆栈。

### 3. AOP 日志埋点
`@log_action` 装饰器自动记录每次操作的参数、执行时间和异常，无需在每个方法里手写日志。

### 4. 软删除 / 回收站机制
- 所有删除操作默认为软删除（`is_delete=1`），数据不会真丢失
- 回收站列表可查看已删除数据
- 支持从回收站恢复
- 永久删除只能针对已在回收站中的数据（双重保险）

### 5. 密码安全
- 密码通过 **bcrypt** 算法哈希后存储，不可逆
- 同层密码长度要求 ≥ 6 位字符
- 密码字段数据库约束 `VARCHAR(255)`，兼容长哈希串

### 6. 防超卖机制
库存表设置 `locked_quantity` 锁定库存字段，为后续下单锁定库存、支付扣减库存的并发控制预留。

---

## 快速开始

### 前置条件
- Python 3.10+
- MySQL 5.7+

### 1. 克隆项目
```bash
cd order-management-system
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库
在项目根目录创建 `.env` 文件：
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=order_management
```

### 4. 启动服务
```bash
# 开发模式（修改代码自动重启）
uvicorn main:app --reload

# 或直接运行
python main.py
```

### 5. 访问接口文档
- **Swagger UI**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## 项目结构

```
order-management-system/
├── main.py                    # 应用入口，路由注册
├── requirements.txt           # 依赖清单
├── .env                       # 环境变量（数据库配置）
│
├── api/                       # API 层：路由分发 + 参数接收
│   ├── product_api.py         # 商品接口
│   ├── order_api.py           # 订单接口
│   ├── stock_api.py           # 库存接口
│   └── user_api.py            # 用户接口
│
├── schema/                    # Schema 层：Pydantic 参数校验
│   ├── product_schema.py      # 商品校验
│   ├── order_schema.py        # 订单校验
│   ├── stock_schema.py        # 库存校验
│   └── user_schema.py         # 用户校验
│
├── service/                   # Service 层：业务逻辑
│   ├── product_service.py     # 商品业务
│   ├── order_service.py       # 订单业务
│   ├── stock_service.py       # 库存业务
│   └── user_service.py        # 用户业务
│
├── dao/                       # DAO 层：数据访问（纯SQL）
│   ├── product_dao.py         # 商品数据操作
│   ├── order_dao.py           # 订单数据操作
│   ├── stock_dao.py           # 库存数据操作
│   └── user_dao.py            # 用户数据操作
│
├── model/                     # Model 层：数据库表映射
│   ├── product.py             # 商品表
│   ├── order_info.py          # 订单表
│   ├── stock.py               # 库存表
│   └── user.py                # 用户表
│
├── core/                      # 核心基础设施
│   ├── db.py                  # 数据库引擎 + Session工厂 + 依赖注入
│   ├── exception.py           # 全局异常体系（分层异常设计）
│   ├── error_handler.py       # 异常降级处理器
│   ├── logger.py              # AOP 日志装饰器
│   ├── response.py            # 统一响应格式
│   └── security.py            # bcrypt 密码加密
│
├── app/                       # 应用配置
│   └── settings.py            # .env 配置读取 (pydantic-settings)
│
└── utils/                     # 工具类
    ├── common.py              # 通用工具函数
    └── snowflake.py           # 雪花算法（生成唯一ID/订单号）
```

---

## 开发约定

### 分层原则
| 层 | 可以做什么 | 不可以做什么 |
|----|-----------|-------------|
| API | 接收参数、调用Service、包装响应 | **不能写业务逻辑、不能写SQL** |
| Schema | 用Pydantic声明字段约束 | 不查数据库 |
| Service | 校验链、业务判断、调用DAO | **不能写SQL、不能操作HTTP** |
| DAO | 执行SQL、增删改查 | **不能做业务判断** |
| Model | 定义表结构和字段映射 | 不写逻辑 |

### 校验链原则
Service 层的校验必须按这个顺序：
1. **非空校验**（内存操作，最快）
2. **范围/格式校验**（内存操作）
3. **唯一性/存在性校验**（查数据库，最慢）

这样在最坏情况（参数错误）下不浪费任何数据库查询。

### 命名规范
- 文件名：`snake_case`（如 `product_service.py`）
- 类名：`PascalCase`（如 `ProductService`）
- 方法名：`snake_case`（如 `create_product`）
- 数据库字段：`snake_case`（如 `product_no`）

---

## 安全红线

- 密码必须通过 `get_password_hash()` 哈希后存储，**严禁明文入库**
- 用户名和邮箱全局唯一，创建/更新时会检查唯一性
- 跨用户操作时需校验数据归属（权限校验预留）
- 永久删除只能针对回收站中的数据（防止误删）