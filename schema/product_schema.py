from pydantic import BaseModel

class ProductCreate(BaseModel):
    product_no : str 
    name : str
    price : int
    stock : int
    
class ProductUpdate(BaseModel):
    product_no : str |None = None
    name : str |None = None
    price : int |None = None
    stock : int |None = None
