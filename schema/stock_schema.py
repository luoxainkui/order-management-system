"""
库存模块 Schema 请求参数校验
============================
Pydantic 校验规则定义
"""
from pydantic import BaseModel, Field
from typing import Optional


# ======================================================================
# 创建库存参数
# ======================================================================

class StockCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="关联商品ID")
    warehouse: Optional[str] = Field(None, max_length=50, description="仓库名称")
    quantity: int = Field(0, ge=0, description="库存数量")
    locked_quantity: int = Field(0, ge=0, description="锁定库存数量")

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": 1,
                "warehouse": "广西饲料仓",
                "quantity": 500,
                "locked_quantity": 0
            }
        }
    }


# ======================================================================
# 更新库存参数
# ======================================================================

class StockUpdate(BaseModel):
    warehouse: Optional[str] = Field(None, max_length=50, description="仓库名称")
    quantity: Optional[int] = Field(None, ge=0, description="库存数量")
    locked_quantity: Optional[int] = Field(None, ge=0, description="锁定库存数量")

    model_config = {
        "json_schema_extra": {
            "example": {
                "quantity": 450
            }
        }
    }