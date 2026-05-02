"""
商品模块 业务逻辑层
===================
整个系统最体现功力的地方

这里是真正的防御式编程训练场
能想到的边界情况都在这里校验

【核心设计】: 校验执行顺序 - 从快到慢
  1. 非空校验 (内存操作, 最快)
  2. 长度/格式校验 (内存操作)
  3. 唯一性校验 (查数据库, 最慢)
  
这就是细节上的性能优化!
"""
from dao.product_dao import ProductDAO
from sqlalchemy.orm import Session
from schema.product_schema import ProductCreate, ProductUpdate
from model.product import Product
from core.logger import log_action
from core.exception import ValidationException,BusinessException,NotFoundException


class ProductService:
    """
    商品业务逻辑静态类
    
    所有方法都是无状态的
    接收db作为第一个参数
    """

    # ======================================================================
    # 基础 CRUD 方法
    # ======================================================================

    @staticmethod
    @log_action("创建商品")
    def create_product(db: Session, product_create: ProductCreate) -> Product:
        """
        创建商品 - 最完整的业务校验链
        """
        product_no = product_create.product_no.strip()
        if not product_no:
            raise ValidationException("商品编号不能为空")
        if len(product_no) > 50:
            raise ValidationException("商品编号不能超过50个字符")
        
        exists_no = ProductDAO.query_no_product(db, product_no)
        if exists_no:
            raise BusinessException("商品编号已存在")
        
        name = product_create.name.strip()
        if not name:
            raise ValidationException("商品名称不能为空")
        if len(name) > 100:
            raise ValidationException("商品名称不能超过100个字符")
        
        exists_name = ProductDAO.query_name_product(db, name)
        if exists_name:
            raise BusinessException("商品名称已存在")
        
        if product_create.price < 0:
            raise ValidationException("商品价格不能小于0")
        
        if product_create.stock < 0:
            raise ValidationException("商品库存不能小于0")
        
        return ProductDAO.create_product(db, product_create)

    @staticmethod
    @log_action("查询商品")
    def query_product(db: Session, product_id: int) -> Product:
        """
        查询单个商品
        
        这里没权限, 所有人都能看商品
        但还是要判断存在性, 给个友好的提示
        """
        product = ProductDAO.query_product(db, product_id)
        if not product:
            raise NotFoundException("商品不存在")
        return product

    @staticmethod
    @log_action("查询商品列表")
    def query_list(
        db: Session,
        page: None | str | int,
        size: None | str | int,
        name: str | None = None
    ) -> dict:
        """
        分页查询商品列表, 带参数容错
        """
        try:
            page = int(page) if page not in (None, "") else 1
            size = int(size) if size not in (None, "") else 10
            
            page = max(page, 1)
            size = min(size, 100)
            
            return ProductDAO.list_product(db, page=page, size=size, name=name)
        except Exception:
            return {
                "list": [],
                "page": 1,
                "size": 10,
                "total": 0,
                "total_pages": 0
            }

    @staticmethod
    @log_action("更新商品")
    def update_product(
        db: Session,
        product_id: int,
        product_update: ProductUpdate
    ) -> Product:
        """
        更新商品信息
        
        重要细节: 改名称/编号时要排除自己, 不然会误报"已存在"
        """
        product = ProductService.query_product(db, product_id)
        update_data = product_update.model_dump(exclude_unset=True)
        
        if "product_no" in update_data:
            product_no = str(update_data["product_no"]).strip()
            exists = ProductDAO.query_no_product(db, product_no)
            if exists and exists.id != product_id:
                raise BusinessException("商品编号已存在")
        
        if "name" in update_data:
            name = str(update_data["name"]).strip()
            exists = ProductDAO.query_name_product(db, name)
            if exists and exists.id != product_id:
                raise BusinessException("商品名称已存在")
        
        if "price" in update_data and update_data["price"] < 0:
            raise ValidationException("商品价格不能小于0")
        
        if "stock" in update_data and update_data["stock"] < 0:
            raise ValidationException("商品库存不能小于0")
        
        return ProductDAO.update_product(db, product_id, update_data)

    @staticmethod
    @log_action("删除商品")
    def delete_product(db: Session, product_id: int) -> bool:
        """
        软删除商品
        
        注意: 只是标记删除状态, 不会真删除记录
        """
        ProductService.query_product(db, product_id)
        return ProductDAO.delete_product(db, product_id)

    # ======================================================================
    # 回收站相关方法
    # ======================================================================

    @staticmethod
    @log_action("查询回收站列表")
    def deleted_list(
        db: Session,
        page: None | str | int,
        size: None | str | int,
        name: str | None = None
    ) -> dict:
        """
        查询回收站商品列表
        """
        try:
            page = int(page) if page not in (None, "") else 1
            size = int(size) if size not in (None, "") else 10
            
            page = max(page, 1)
            size = min(size, 100)
            
            return ProductDAO.deleted_list(db, page=page, size=size, name=name)
        except Exception:
            return {
                "list": [],
                "page": 1,
                "size": 10,
                "total": 0,
                "total_pages": 0
            }

    @staticmethod
    @log_action("恢复商品")
    def restore_product(db: Session, product_id: int) -> bool:
        """
        从回收站恢复商品
        """
        product = ProductDAO.query_deleted_product(db, product_id)
        if not product:
            raise NotFoundException("回收站中不存在该商品")
        
        return ProductDAO.restore_product(db, product_id)

    @staticmethod
    @log_action("永久删除商品")
    def hard_delete_product(db: Session, product_id: int) -> bool:
        """
        永久删除商品 (不可逆!)
        
        安全机制: 只能删除【已经在回收站】的商品
        """
        product = ProductDAO.query_deleted_product(db, product_id)
        if not product:
            raise BusinessException("只能永久删除回收站中的商品")
        
        return ProductDAO.hard_delete_product(db, product_id)
