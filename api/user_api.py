"""
用户模块 API 接口层
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
from service.user_service import UserService
from sqlalchemy.orm import Session
from core.db import get_db
from core.response import success
from schema.user_schema import UserCreate, UserUpdate


router = APIRouter(prefix="/api/v1/users", tags=["用户相关接口"])


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
# 用户基础 CRUD 接口
# ======================================================================

@router.get("/{user_id}", summary="获取用户详情")
def get_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    """
    根据ID查询单个用户详情
    """
    user = UserService.query_user(db, user_id)
    return success(user, "查询成功")


@router.get("/list", summary="获取用户列表")
def list_user(
    page_info: tuple[int, int] = Depends(page_params),
    db: Session = Depends(get_db)
) -> dict:
    page, size = page_info
    data = UserService.query_list(db, page=page, size=size)
    return success(data, "查询成功")


@router.post("/create", summary="创建用户")
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> dict:
    """
    创建新用户
    """
    user = UserService.create_user(db, user_in)
    return success(user, "创建成功")


@router.put("/{user_id}", summary="修改用户")
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    根据ID修改用户信息
    """
    user = UserService.update_user(db, user_id, user_in)
    return success(user, "修改成功")


@router.delete("/{user_id}", summary="删除用户")
def delete_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    """
    软删除用户
    """
    UserService.delete_user(db, user_id)
    return success(msg="删除成功")


# ======================================================================
# 回收站相关接口
# ======================================================================

@router.get("/deleted/list", summary="获取回收站用户列表")
def deleted_list(
    page_info: tuple[int, int] = Depends(page_params),
    db: Session = Depends(get_db)
) -> dict:
    page, size = page_info
    data = UserService.deleted_list(db, page=page, size=size)
    return success(data, "查询成功")


@router.put("/restore/{user_id}", summary="恢复回收站用户")
def restore_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    """
    从回收站恢复用户
    """
    UserService.restore_user(db, user_id)
    return success(msg="恢复成功")


@router.delete("/hard/{user_id}", summary="永久删除用户")
def hard_delete_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    """
    永久删除用户 (不可逆!)
    """
    UserService.hard_delete_user(db, user_id)
    return success(msg="永久删除成功")