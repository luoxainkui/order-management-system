# 导入模型商品表
from model.product import Product
# 导入前端传参数据
from schema.product_schema import ProductCreate
# 导入时间
from datetime import datetime as dt
# 导入数据库
from sqlalchemy.orm import Session


class ProductDAO:
    """ 商品表业务 """
    @staticmethod
    def query_product(db:Session,product:int,*,include_deleted:bool=False,only_deleted:bool=False) ->Product|None:
        """
        根据商品ID查询商品
        :param db: 数据库会话
        :param product_id: 商品ID
        :param include_deleted: 是否包含软删除商品
        :param only_deleted: 仅查询软删除商品
        :return: 商品实体,不存在则返回None
        """
        query = db.query(Product).filter(Product.id == product)
        if only_deleted:
            query = query.filter(Product.is_delete_prod == 1)
        elif not include_deleted:
            query = query.filter(Product.is_delete_prod == 0)
        return query.first()
    
    @staticmethod
    def list_product(db:Session,page: int = 1, size: int = 10, name_id: int | None = None) ->dict:
        """
        分页查询商品列表
        :param page: 第几页(默认第1页)
        :param size: 每页显示几条(默认10条)
        :param user_id: 可选的用户ID过滤
        :return 字典(包含分页信息+当前页数据列表)
        """
        skip = (page-1)*size
        query = db.query(Product).filter(Product.is_delete_prod ==0)
        if name_id is not None:
            query = query.filter(Product.name_id == name_id)
        product_list = query.offset(skip).limit(size),all()
        total = query.count()
        total_pages = (total+size -1) //size
        return {
            "list" : product_list, # 当前页数据
            "page" : page, # 当前页码
            "size" : size, # 每页条数
            "total" : total,  # 总条数
            "total_pages" : total_pages #总页数
        }

    # @staticmethod
    # def create_product(db:Session,product_create:ProductCreate):
    #     date = 