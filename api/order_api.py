# 传入逻辑
from service.order_service import OrderService
# 传入第三方库
from fastapi import APIRouter,Depends,Query
# 导入数据库会话类型
from sqlalchemy.orm import Session
# 导入数据库会话依赖
from core.db import get_db
# 导入订单创建和更新的前端数据模型
from schema.order_schema import OrderCreate,OrderUpdate
# 导入登入用户ID
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
    :权限: 只查自己订单
    """
    page,size = page_info
    data = OrderService.query_list(db,page=page,size=size,current_user_id=current_user_id)
    return {
        "code": 200,
        "msg": "查询成功",
        "data":data
    }

@router.post("/create",summary="创建订单")
def create_order(
    order_in: OrderCreate,
    db:Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) ->dict[str,any]:
    """
    创建订单接口
    业务层会自动校验：价格范围、订单号是否重复、数据合法性
    并绑定当前登录用户为订单所属人
    """
    order = OrderService.create_order(db,order_in,current_user_id)
    return {
        "code":200,
        "msg": "创建成功",
        "data": order
    }

@router.put("/{order_id}",summary="修改订单")
def update_order(
    order_id: int,
    order_in: OrderUpdate,
    db:Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) ->dict[str,any]:
    """
    修改订单信息
    校验：订单存在 + 属于当前用户 + 新数据合法（价格、订单号不重复等)
    """
    updated_order = OrderService.update_order(db,order_id,order_in,current_user_id)
    return {
        "code": 200,
        "msg": "修改成功",
        "data": updated_order
    }

@router.delete("/{order_id}",summary="软删除订单")
def delete_order(
    order_id: int,
    db:Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) ->dict[str,any]:
    """
    软删除订单（并非真删除，只是标记 is_delete=1
    校验：订单存在 + 属于当前用户
    删除后数据进入回收站，可恢复
    """
    OrderService.delete_order(db,order_id,current_user_id)
    return {
        "code": 200,
        "msg": "删除成功",
        "data": None
    }

@router.get("/deleted/list",summary="获取回收站订单列表")
def deleted_order_list(
    page_info: tuple[int,int] = Depends(page_params),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) ->dict[str,any]:
    """
    分页查询【回收站】里的订单（只查询已软删除的数据）
    只能查看自己删除的订单
    """
    page,size = page_info
    data = OrderService.deleted_list(db,page=page,size=size,current_user_id=current_user_id)
    return {
        "code": 200,
        "msg": "查询回收站成功",
        "data":data
    }

@router.post("/{order_id}/restore",summary="恢复订单")
def restore_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) ->dict[str,any]:
    """
    从回收站恢复订单（取消软删除标记）
    """
    OrderService.restore_order(db,order_id,current_user_id)
    return {
        "code": 200,
        "msg": "恢复成功",
        "data":None
    }

@router.delete("/{order_id}/hard",summary="永久删除订单")
def hard_delete_order(
    order_id: int,
    db:Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) ->dict[str,any]:
    """
    永久删除订单（彻底从数据库删除，无法恢复）
    """
    OrderService.hard_delete_order(db,order_id,current_user_id)
    return {
        "code": 200,
        "msg": "永久删除订单",
        "data": None
    }