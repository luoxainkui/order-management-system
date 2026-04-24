from pydantic import BaseModel

class ProductCreate(BaseModel):
    prduct_no : str 
    name_id : str
    price : int|float
    stock : int
    
class ProductUpdate(BaseModel):
    prduct_no : str |None = None
    name_id : str |None = None
    price : int|float |None = None
    stock : int |None = None
