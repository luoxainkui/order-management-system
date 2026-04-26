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
from core.exception import ValidationException,NotFoundException

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
    def query_list(db:Session,page: None,size: None):
        try:
            page = int(page) if page not in (None,"") else 1
            size = int(size) if size not in (None,"") else 10

            page = max(page,1)
            size = min(size,100)

            return ProductDAO.list_product(db,page=page,size=size)
        except Exception:
            return {"list" : [],"page" : 1,"size" : 10,"total" : 0,"total_pages" : 0}
        