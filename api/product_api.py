"""
商品模块 API 接口层
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
from service.product_service import ProductService
from sqlalchemy.orm import Session
from core.db import get_db
from core.response import success
from schema.product_schema import ProductCreate, ProductUpdate


router = APIRouter(prefix="/api/v1/products", tags=["商品相关接口"])


def page_params(
    page: int | None = Query(1, ge=1, description="页码, 默认1"),
    size: int | None = Query(10, ge=1, le=100, description="每页条数, 默认10, 最大100")
):
    """
    【分页参数公共依赖】
    """
    page = max(page or 1, 1)
    size = max(min(size or 10, 100), 1)
    return page, size


# ======================================================================
# 商品基础 CRUD 接口
# ======================================================================

@router.get("/{product_id}", summary="获取商品详情")
def get_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    """
    根据ID查询单个商品详情
    """
    product = ProductService.query_product(db, product_id)
    return success(product, "查询成功")


@router.get("/list", summary="获取商品列表")
def list_product(
    page_info: tuple[int, int] = Depends(page_params),
    name: str | None = Query(None, description="商品名称模糊搜索"),
    db: Session = Depends(get_db)
) -> dict:
    page, size = page_info
    data = ProductService.query_list(db, page=page, size=size, name=name)
    return success(data, "查询成功")


@router.post("/create", summary="创建商品")
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)) -> dict:
    """
    创建新商品
    """
    product = ProductService.create_product(db, product_in)
    return success(product, "创建成功")


@router.put("/{product_id}", summary="修改商品")
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    根据ID修改商品信息
    """
    product = ProductService.update_product(db, product_id, product_in)
    return success(product, "修改成功")


@router.delete("/{product_id}", summary="删除商品")
def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    """
    软删除商品
    """
    ProductService.delete_product(db, product_id)
    return success(msg="删除成功")


# ======================================================================
# 回收站相关接口
# ======================================================================

@router.get("/deleted/list", summary="获取回收站商品列表")
def deleted_list(
    page_info: tuple[int, int] = Depends(page_params),
    name: str | None = Query(None, description="商品名称模糊搜索"),
    db: Session = Depends(get_db)
) -> dict:
    page, size = page_info
    data = ProductService.deleted_list(db, page=page, size=size, name=name)
    return success(data, "查询成功")


@router.put("/restore/{product_id}", summary="恢复回收站商品")
def restore_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    """
    从回收站恢复商品到正常状态
    """
    ProductService.restore_product(db, product_id)
    return success(msg="恢复成功")


@router.delete("/hard/{product_id}", summary="永久删除商品")
def hard_delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    """
    永久删除商品 (不可逆!)
    """
    ProductService.hard_delete_product(db, product_id)
    return success(msg="永久删除成功")
