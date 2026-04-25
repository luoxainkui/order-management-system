from pydantic import BaseModel

class ProductCreate(BaseModel):
    product_no : str 
    name : str
    price : int|float
    stock : int
    
class ProductUpdate(BaseModel):
    product_no : str |None = None
    name : str |None = None
    price : int|float |None = None
    stock : int |None = None
