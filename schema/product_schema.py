from pydantic import BaseModel

class ProductCreate(BaseModel):
    prduct_no = str 
    