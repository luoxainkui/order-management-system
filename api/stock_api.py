"""
库存模块 API 接口层
==================
分层架构的第一层：入口网关

设计原则: API层只做3件事
  1. 接收参数 (路径参数/查询参数/请求体)
  2. 调用 Service 层的业务方法
  3. 包装统一返回格式

反模式: API层千万不要写业务逻辑!
         不要在这里写if判断、不要写SQL!
"""
from fastapi import APIRouter, Depends, Query
from service.stock_service import StockService
from sqlalchemy.orm import Session
from core.db import get_db
from core.response import success
from schema.stock_schema import StockCreate, StockUpdate


router = APIRouter(prefix="/api/v1/stocks", tags=["库存相关接口"])


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
# 库存基础 CRUD 接口
# ======================================================================

@router.get("/{stock_id}", summary="获取库存详情")
def get_stock(stock_id: int, db: Session = Depends(get_db)) -> dict:
    """
    根据ID查询单条库存记录
    """
    stock = StockService.query_stock(db, stock_id)
    return success(stock, "查询成功")


@router.get("/list", summary="获取库存列表")
def list_stock(
    page_info: tuple[int, int] = Depends(page_params),
    db: Session = Depends(get_db)
) -> dict:
    page, size = page_info
    data = StockService.query_list(db, page=page, size=size)
    return success(data, "查询成功")


@router.post("/create", summary="创建库存")
def create_stock(stock_in: StockCreate, db: Session = Depends(get_db)) -> dict:
    """
    创建新库存记录
    """
    stock = StockService.create_stock(db, stock_in)
    return success(stock, "创建成功")


@router.put("/{stock_id}", summary="修改库存")
def update_stock(
    stock_id: int,
    stock_in: StockUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    根据ID修改库存信息
    """
    stock = StockService.update_stock(db, stock_id, stock_in)
    return success(stock, "修改成功")


@router.delete("/{stock_id}", summary="删除库存")
def delete_stock(stock_id: int, db: Session = Depends(get_db)) -> dict:
    """
    软删除库存记录
    """
    StockService.delete_stock(db, stock_id)
    return success(msg="删除成功")


# ======================================================================
# 回收站相关接口
# ======================================================================

@router.get("/deleted/list", summary="获取回收站库存列表")
def deleted_list(
    page_info: tuple[int, int] = Depends(page_params),
    db: Session = Depends(get_db)
) -> dict:
    page, size = page_info
    data = StockService.deleted_list(db, page=page, size=size)
    return success(data, "查询成功")


@router.put("/restore/{stock_id}", summary="恢复回收站库存")
def restore_stock(stock_id: int, db: Session = Depends(get_db)) -> dict:
    """
    从回收站恢复库存记录
    """
    StockService.restore_stock(db, stock_id)
    return success(msg="恢复成功")


@router.delete("/hard/{stock_id}", summary="永久删除库存")
def hard_delete_stock(stock_id: int, db: Session = Depends(get_db)) -> dict:
    """
    永久删除库存记录 (不可逆!)
    """
    StockService.hard_delete_stock(db, stock_id)
    return success(msg="永久删除成功")