# utils/common.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 1. 定义 Token 获取 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    全局依赖:获取当前登录用户ID
    :param token: 从请求头自动获取的Token
    :return: 用户ID
    """
    try:
        # 【开发调试模式】
        # 实际生产环境：这里写 JWT 解密逻辑
        # 例如：user_id = jwt_decode(token)
        return 1 
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="身份验证失败，请重新登录"
        )

# 通用函数（时间格式化）
def format_datetime(dt_obj):
    return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
