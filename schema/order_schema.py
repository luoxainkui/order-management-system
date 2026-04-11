# 插入转义库
from pydantic import BaseModel
class OrderCreate(BaseModel):

    order_no : str 
    total_price = float
    status = str