# 导入商品业务
from dao.product_dao import ProductDAO
# 导入数据会话
from sqlalchemy.orm import Session
# 导入前段传参
from schema.product_schema import ProductCreate,ProductUpdate
# 导入模型
from model.product import Product
# 导入日志
from core.logger import log_action
# 导入异常
from core.exception import ValidationException,NotFoundException,BusinessException

class ProductService:
    """ 商品逻辑层"""
    @staticmethod
    def query_product(db:Session,product_id:int) ->Product:
        """
        根据商品ID查询商品,并校验当前用户是否有权限访问

        :param db: 数据库会话
        :param product_id: 订单ID
        :return: 商品对象,或抛出 NotFoundException
        """
        product = ProductDAO.query_product(db,product_id)
        if not product:
            raise NotFoundException("商品不存在")
        return product
    
    @staticmethod
    @log_action("查询商品列表")
    def query_list(db:Session,page: None,size: None) ->dict:
        """
        分页查询商品列表,用于页面展示

        :param db: 数据库会话
        :param page: 页码(异常或空值时默认1)
        :param size: 每页条数(异常或空值时默认10)
        :return: 包含分页信息的字典
        """
        try:
            page = int(page) if page not in (None,"") else 1
            size = int(size) if size not in (None,"") else 10

            page = max(page,1)
            size = min(size,100)

            return ProductDAO.list_product(db,page=page,size=size)
        except Exception:
            return {"list" : [],"page" : 1,"size" : 10,"total" : 0,"total_pages" : 0}
        
    @staticmethod
    @log_action("查询已删除商品列表")
    def deleted_list(db:Session,page:None,size:None) ->dict:
        """
        分页查询已软删除商品,用于回收站页面展示

        :param db: 数据库会话
        :param page: 页码(异常或空值时默认1)
        :param size: 每页条数(异常或空值时默认10)
        :return: 包含回收站分页数据的字典
        """
        try:
            page = int(page) if page not in (None,"") else 1
            size = int(size) if size not in (None,"") else 10

            page = max(page,1)
            size = min(size,10)

            return ProductDAO.deleted_list(db,page=page,size=size)
        except Exception:
            return {"list" : [],"page" : 1,"size" : 10,"total" : 0,"total_pages" : 0}
        
    @staticmethod
    @log_action("创建商品")
    def create_product(db:Session,product_create:ProductCreate) ->Product:
        """
        创建商品并执行校验：名称非空、长度限制、名称查重、价格校验、库存校验

        :param db: 数据库会话
        :param product_create: 前端传入的商品数据
        :return: 创建成功的商品对象
        :raises ValidationException: 字段不合法、为空、长度超限、数值小于0
        :raises BusinessException: 商品名称已存在
        """
        name = product_create.name.strip()
        if not name:
            raise ValidationException("商品名称不为空")
        if len(name)>100:
            raise ValidationException("商品名称字符大于100!")
        
        exists = ProductDAO.query_name_product(db,name)
        if exists:
            raise BusinessException("商品名称已经存在")
        
        price = product_create.price
        if not isinstance(price,int) or price<0:
            raise ValidationException("商品价格不能小于0")
        
        stock = product_create.stock
        if stock<0:
            raise ValidationException("商品库存不能小于0")
        
        return  ProductDAO.create_product(db,product_create)
    
    @staticmethod
    @log_action("修改商品")
    def update_product(db:Session,product_id:int,update_data:ProductUpdate) ->Product:
        """
        修改商品信息,校验商品是否存在、字段合法性、名称查重、空字段判断
    
        :param db: 数据库会话
        :param product_id: 要修改的商品ID
        :param update_data: 前端传入的更新数据
        :return: 更新后的商品对象
        :raises NotFoundException: 商品不存在
        :raises ValidationException: 字段不合法|无更新字段
        :raises BusinessException: 商品名称重复
        """
        product = ProductDAO.query_product(db,product_id)
        if not product:
            raise NotFoundException("商品不存在")
        
        data = update_data.model_dump(exclude_unset=True)
        if  not data:
            raise ValidationException("没有可更新的字段")
        
        if "name" in data:
            name = data["name"]
            if name is not None:
                name = name.strip()
            if not name:
                raise ValidationException("商品名称不能为空")
            if len(name)>100:
                raise ValidationException("商品名称字符大于100!")
            
            exists = ProductDAO.query_name_product(db,name)
            if exists and exists.id != product_id:
                raise BusinessException("商品名称已经存在")
            
        if "price" in data:
            price = data['price']
            if not isinstance(price,int) or price<0:
                raise ValidationException("商品价格必须为整数且不能小于0")

        if "stock" in data:
            stock = data['stock']
            if stock < 0:
                raise ValidationException("商品库存不能小于0")
        return ProductDAO.update_product(db,product_id,data)

    @staticmethod
    @log_action("软删除商品")
    def delete_product(db:Session,product_id:int) ->bool:
        """
        软删除商品（不会真删除，只标记删除状态）
        :param db: 数据库会话
        :param product_id: 商品ID
        :return: 删除成功返回 True
        :raises NotFoundException: 商品不存在
        :raises BusinessException: 删除失败
        """
        product = ProductDAO.query_product(db,product_id)
        if not product:
            raise NotFoundException("商品不存在")

        success = ProductDAO.delete_product(db,product_id)
        if not success:
            raise BusinessException("删除失败")

        return True

    @staticmethod
    @log_action("恢复商品")
    def restore_prouct(db:Session,product_id:int):
        product = 















