# 插入转义库
from pydantic import BaseModel
class OrderCreate(BaseModel):
    """
    :prder_on: 订单
    :total_price: 总计价格
    :status: 状态
    """
    order_no : str 
    total_price = float
    status = str | None = "待支付"
    user_id = int | None = None

# 继承
class OrderUpdate(OrderCreate):
    """
    继承状态
    """
    order_no : str | None = None
    total_price : float | None | int = None
    status : str | None = None
    user_id = str | None = None