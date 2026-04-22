# 传入业务
from dao.order_dao import OrderDAO
# 传入日志
from core.logger import log_action
# 传入逻辑
from service.order_service import OrderService
# 传入时间
from datetime import datetime as dt 
# 传入第三方库
from fastapi import APIRouter,Depends,Query
# 导入数据库会话类型
from sqlalchemy.orm import Session
# 导入数据库会话依赖
from core.db import get_db
# 导入订单创建和更新的前端数据模型
from schema.order_schema import OrderCreate,OrderUpdate

from utils.common import get_current_user_id


router = APIRouter(prefix="/api/v1/orders",tags=["订单相关接口"])

def page_params(
    page: int | None = Query(1, ge=1, description="页码,默认1"),
    size: int | None = Query(10, ge=1, le=100, description="每页条数.默认10,最大100")
) -> tuple[int,int]:
    """
    解析分页参数的依赖函数
    :param page: 页码
    :param size: 每页条数
    :return: 返回解析后的页码和每页条数
    """
    page = max(page or 1,1)
    size = max(min(size or 10,100),1)
    return page,size

@router.get("/{order_id}", summary="获取订单详情")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) ->dict[str,any]:
    """
    获取订单详情接口
    :param order_id: 订单ID
    :param db: 数据库会话
    :param current_user_id: 当前登录用户ID
    :return: 订单详情对象或错误信息
    """
    order = OrderService.query_order(db,order_id,current_user_id)
    return {
        "code": 200,
        "msg": "查询成功",
        "data":order
    }
    
@router.get("/list",summary="获取订单列表")
def list_order(
    page_info:tuple[int,int] = Depends(page_params),
    db:Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) ->dict[str,any]:
    """
    分页查询当前用户的订单列表
    """
    page,size = page_info
    data = OrderService.query_list(db,page=page,size=size,current_user_id=current_user_id)
    return {
        "code": 200,
        "msg": "查询成功",
        "data":data
    }






