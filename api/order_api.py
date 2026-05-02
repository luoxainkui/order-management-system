"""
订单模块 API 接口层
==================
与商品模块最大的区别: 所有订单接口都需要用户登录校验
每个用户只能看到和操作自己的订单, 这就是【数据权限】

数据权限是企业级系统必备设计:
  A用户绝对不能修改B用户的订单
"""
from fastapi import APIRouter, Depends, Query
from service.order_service import OrderService
from sqlalchemy.orm import Session
from core.db import get_db
from core.response import success
from schema.order_schema import OrderCreate, OrderUpdate
from utils.common import get_current_user_id


router = APIRouter(prefix="/api/v1/orders", tags=["订单相关接口"])


def page_params(
    page: int | None = Query(1, ge=1, description="页码, 默认1"),
    size: int | None = Query(10, ge=1, le=100, description="每页条数, 默认10, 最大100")
) -> tuple[int, int]:
    """
    分页参数公共依赖 (全局统一, 每个模块都一样)
    """
    page = max(page or 1, 1)
    size = max(min(size or 10, 100), 1)
    return page, size


# ======================================================================
# 订单基础 CRUD 接口
# ======================================================================

@router.get("/{order_id}", summary="获取订单详情")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> dict:
    order = OrderService.query_order(db, order_id, current_user_id)
    return success(order, "查询成功")


@router.get("/list", summary="获取订单列表")
def list_order(
    page_info: tuple[int, int] = Depends(page_params),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> dict:
    page, size = page_info
    data = OrderService.query_list(db, page=page, size=size, current_user_id=current_user_id)
    return success(data, "查询成功")


@router.post("/create", summary="创建订单")
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> dict:
    order = OrderService.create_order(db, order_in, current_user_id)
    return success(order, "创建成功")


@router.put("/{order_id}", summary="修改订单")
def update_order(
    order_id: int,
    order_in: OrderUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> dict:
    order = OrderService.update_order(db, order_id, order_in, current_user_id)
    return success(order, "修改成功")


@router.delete("/{order_id}", summary="删除订单")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> dict:
    OrderService.delete_order(db, order_id, current_user_id)
    return success(msg="删除成功")


# ======================================================================
# 回收站相关接口
# ======================================================================

@router.get("/deleted/list", summary="获取回收站订单列表")
def deleted_list(
    page_info: tuple[int, int] = Depends(page_params),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> dict:
    page, size = page_info
    data = OrderService.deleted_list(db, page=page, size=size, current_user_id=current_user_id)
    return success(data, "查询成功")


@router.put("/restore/{order_id}", summary="恢复回收站订单")
def restore_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> dict:
    OrderService.restore_order(db, order_id, current_user_id)
    return success(msg="恢复成功")


@router.delete("/hard/{order_id}", summary="永久删除订单")
def hard_delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> dict:
    OrderService.hard_delete_order(db, order_id, current_user_id)
    return success(msg="永久删除成功")
