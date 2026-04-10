from pydantic import BaseModel

class OrderCreate(BaseModel):
    order_no : str 
    total_price = float
    status = str