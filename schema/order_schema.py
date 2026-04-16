from pydantic import BaseModel

class OrderCreate(BaseModel):
    """创建订单请求模型"""
    order_no: str
    total_price: float
    status: str | None = "待支付"
    user_id: int | None = None

class OrderUpdate(BaseModel):
    """更新订单请求模型，所有字段均可选。"""
    order_no: str | None = None
    total_price: float | int | None = None
    status: str | None = None
    user_id: int | None = None