"""
用户模块 业务逻辑层
==================
防御式编程完整校验链

【核心设计】: 校验执行顺序 - 从快到慢
  1. 非空校验 (内存操作, 最快)
  2. 长度/格式校验 (内存操作)
  3. 唯一性校验 (查数据库, 最慢)

【安全红线】:
  - 密码绝对不能明文存库, 必须 bcrypt 哈希
  - 用户名/邮箱全局唯一, 防止重复注册
"""
from dao.user_dao import UserDAO
from sqlalchemy.orm import Session
from schema.user_schema import UserCreate, UserUpdate
from model.user import User
from core.logger import log_action
from core.exception import ValidationException, BusinessException, NotFoundException
from core.security import get_password_hash


class UserService:
    """
    用户业务逻辑静态类

    所有方法都是无状态的, 接收 db 作为第一个参数
    """

    # ======================================================================
    # 基础 CRUD 方法
    # ======================================================================

    @staticmethod
    @log_action("创建用户")
    def create_user(db: Session, user_create: UserCreate) -> User:
        """
        创建新用户

        校验链: 参数非空 → 唯一性 → 密码哈希
        """
        username = user_create.username.strip()
        if not username:
            raise ValidationException("用户名不能为空")

        email = user_create.email.strip()
        if not email:
            raise ValidationException("邮箱不能为空")

        password = user_create.password
        if not password or len(password) < 6:
            raise ValidationException("密码至少需要6个字符")

        exists_username = UserDAO.query_by_username(db, username)
        if exists_username:
            raise BusinessException("用户名已存在")

        exists_email = UserDAO.query_by_email(db, email)
        if exists_email:
            raise BusinessException("邮箱已被注册")

        user_create.password = get_password_hash(password)

        return UserDAO.create_user(db, user_create)

    @staticmethod
    @log_action("查询用户")
    def query_user(db: Session, user_id: int) -> User:
        """
        查询单个用户
        """
        user = UserDAO.query_user(db, user_id)
        if not user:
            raise NotFoundException("用户不存在")
        return user

    @staticmethod
    @log_action("查询用户列表")
    def query_list(
        db: Session,
        page: None | str | int,
        size: None | str | int
    ) -> dict:
        """
        分页查询用户列表, 带参数容错
        """
        try:
            page = int(page) if page not in (None, "") else 1
            size = int(size) if size not in (None, "") else 10

            page = max(page, 1)
            size = min(size, 100)

            return UserDAO.list_user(db, page=page, size=size)
        except Exception:
            return {
                "list": [],
                "page": 1,
                "size": 10,
                "total": 0,
                "total_pages": 0
            }

    @staticmethod
    @log_action("更新用户")
    def update_user(
        db: Session,
        user_id: int,
        user_update: UserUpdate
    ) -> User:
        """
        更新用户信息

        校验链: 存在性 → 唯一性(排除自己) → 参数合法性
        """
        UserService.query_user(db, user_id)
        update_data = user_update.model_dump(exclude_unset=True)

        if "username" in update_data:
            username = str(update_data["username"]).strip()
            if not username:
                raise ValidationException("用户名不能为空")
            exists = UserDAO.query_by_username(db, username)
            if exists and exists.id != user_id:
                raise BusinessException("用户名已存在")

        if "email" in update_data:
            email = str(update_data["email"]).strip()
            if not email:
                raise ValidationException("邮箱不能为空")
            exists = UserDAO.query_by_email(db, email)
            if exists and exists.id != user_id:
                raise BusinessException("邮箱已被注册")

        if "password" in update_data:
            password = update_data["password"]
            if len(password) < 6:
                raise ValidationException("密码至少需要6个字符")
            update_data["password"] = get_password_hash(password)

        return UserDAO.update_user(db, user_id, update_data)

    @staticmethod
    @log_action("删除用户")
    def delete_user(db: Session, user_id: int) -> bool:
        """
        软删除用户
        """
        UserService.query_user(db, user_id)
        return UserDAO.delete_user(db, user_id)

    # ======================================================================
    # 回收站相关方法
    # ======================================================================

    @staticmethod
    @log_action("查询回收站用户列表")
    def deleted_list(
        db: Session,
        page: None | str | int,
        size: None | str | int
    ) -> dict:
        """
        查询回收站用户列表
        """
        try:
            page = int(page) if page not in (None, "") else 1
            size = int(size) if size not in (None, "") else 10

            page = max(page, 1)
            size = min(size, 100)

            return UserDAO.deleted_list(db, page=page, size=size)
        except Exception:
            return {
                "list": [],
                "page": 1,
                "size": 10,
                "total": 0,
                "total_pages": 0
            }

    @staticmethod
    @log_action("恢复用户")
    def restore_user(db: Session, user_id: int) -> bool:
        """
        从回收站恢复用户
        """
        user = UserDAO.query_deleted_user(db, user_id)
        if not user:
            raise NotFoundException("回收站中不存在该用户")

        return UserDAO.restore_user(db, user_id)

    @staticmethod
    @log_action("永久删除用户")
    def hard_delete_user(db: Session, user_id: int) -> bool:
        """
        永久删除用户 (不可逆!)

        安全机制: 只能删除【已经在回收站】的用户
        """
        user = UserDAO.query_deleted_user(db, user_id)
        if not user:
            raise BusinessException("只能永久删除回收站中的用户")

        return UserDAO.hard_delete_user(db, user_id)