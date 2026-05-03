"""
用户模块 schema 请求参数校验
============================
Pydantic 校验规则定义
"""
from pydantic import BaseModel, Field
from typing import Optional

# ======================================================================
# 创建用户参数
# ======================================================================        

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: str = Field(..., min_length=1, max_length=100, description="用户邮箱")
    password: str = Field(..., min_length=6, max_length=255, description="用户密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "password123",
                "phone": "13800138000"
            }
        }
    }


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    email: Optional[str] = Field(None, min_length=1, max_length=100, description="用户邮箱")
    password: Optional[str] = Field(None, min_length=6, max_length=255, description="用户密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "testuser@example.com",
                "phone": "13800138000"
            }
        }
    }
