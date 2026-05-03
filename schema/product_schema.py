"""
商品模块 Schema 请求参数校验
============================
Pydantic 校验规则定义
"""
from pydantic import BaseModel, Field
from typing import Optional


# ======================================================================
# 创建商品参数
# ======================================================================

class ProductCreate(BaseModel):
    product_no: Optional[str] = Field(None, min_length=1, max_length=50, description="商品编号(不传则自动生成)")
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    price: int = Field(..., ge=0, le=999999, description="商品价格, 单位: 分")
    stock: int = Field(0, ge=0, le=999999, description="库存数量")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "product_no": "P001",
                "name": "测试商品",
                "price": 9900,
                "stock": 100
            }
        }
    }


# ======================================================================
# 更新商品参数
# ======================================================================

class ProductUpdate(BaseModel):
    product_no: Optional[str] = Field(None, min_length=1, max_length=50, description="商品编号(不传则不修改)")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="商品名称")
    price: Optional[int] = Field(None, ge=0, le=999999, description="商品价格, 单位: 分")
    stock: Optional[int] = Field(None, ge=0, le=999999, description="库存数量")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "修改后的商品名称",
                "price": 19900
            }
        }
    }
