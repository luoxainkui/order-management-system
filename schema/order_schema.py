"""
订单模块 Schema 请求参数校验
============================
Pydantic 校验规则定义

【重要设计】: user_id 不出现在任何Schema里.
             绑定关系在Service层通过token实现.
"""
from pydantic import BaseModel, Field
from typing import Optional


DEFAULT_PENDING_STATUS = "待支付"


# ======================================================================
# 创建订单参数
# ======================================================================

class OrderCreate(BaseModel):
    order_no: str = Field(..., min_length=1, max_length=50, description="订单编号")
    total_price: int = Field(..., ge=0, le=999999, description="订单总金额, 单位: 分")
    status: str = Field(DEFAULT_PENDING_STATUS, min_length=1, max_length=20, description="订单状态")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "order_no": "O202401010001",
                "total_price": 9900,
                "status": "待支付"
            }
        }
    }


# ======================================================================
# 更新订单参数
# ======================================================================

class OrderUpdate(BaseModel):
    total_price: Optional[int] = Field(None, ge=0, le=999999, description="订单总金额, 单位: 分")
    status: Optional[str] = Field(None, min_length=1, max_length=20, description="订单状态")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "已支付"
            }
        }
    }
