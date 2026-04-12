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
    status = str

# 继承
class OrderUpdate(OrderCreate):

    order_no : str |None = None
    total_price : float |None = None
    status : str |None = None