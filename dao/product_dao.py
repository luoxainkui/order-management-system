# 导入模型商品表
from model.product import Product
# 导入前端传参数据
from schema.product_schema import ProductCreate,ProductUpdate
# 导入时间
from datetime import datetime as dt
# 导入数据库
from sqlalchemy.orm import Session


class ProductDAO:
    """ 商品表业务 """
    @staticmethod
    def query_product(db:Session,product_id:int,*,include_deleted:bool=False,only_deleted:bool=False) ->Product|None:
        """
        根据商品ID查询商品
        :param db: 数据库会话
        :param product_id: 商品ID
        :param include_deleted: 是否包含软删除商品
        :param only_deleted: 仅查询软删除商品
        :return: 商品实体,不存在则返回None
        """
        query = db.query(Product).filter(Product.id == product_id)
        if only_deleted:
            query = query.filter(Product.is_delete_prod == 1)
        elif not include_deleted:
            query = query.filter(Product.is_delete_prod == 0)
        return query.first()
    
    @staticmethod
    def list_product(db:Session,page: int = 1, size: int = 10, name: str | None = None) ->dict:
        """
        分页查询商品列表
        :param page: 第几页(默认第1页)
        :param size: 每页显示几条(默认10条)
        :param name: 可选的用户过滤
        :return 字典(包含分页信息+当前页数据列表)
        """
        skip = (page-1)*size
        query = db.query(Product).filter(Product.is_delete_prod ==0)
        if name is not None:
            name = name.strip()
            if name:
                query = query.filter(Product.name.like(f"%{name}%"))
        product_list = query.offset(skip).limit(size).all()
        total = query.count()
        total_pages = (total+size -1) //size
        return {
            "list" : product_list, # 当前页数据
            "page" : page, # 当前页码
            "size" : size, # 每页条数
            "total" : total,  # 总条数
            "total_pages" : total_pages #总页数
        }

    @staticmethod
    def create_product(db:Session,product_create:ProductCreate) ->Product:
        """
        创建商品
        :param product_create: 商品创建数据
        :return: 返回商品对象
        """
        data = product_create.model_dump()
        data["created_time"] = dt.now()
        data["is_delete_prod"] = 0
        product = Product(**data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update_product(db:Session,product_id:int,product_update:ProductUpdate) ->Product|None:
        """
        根据ID更新商品信息
        :param db: 数据库会话
        :param order_id: 商品ID
        :param order_update: 更新数据
        :return: 更新后的商品对象,商品不存在返回 None
        """
        product =db.query(Product).filter(Product.id == product_id,Product.is_delete_prod == 0).first()
        if not product:
            return None
        update_data = product_update.model_dump(exclude_unset=True)
        if not update_data:
            return product
        for key,value in update_data.items():
            setattr(product,key,value)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db:Session,product_id:int) ->Product|None:
        """
        软删除,仅为标记
        :param db: 数据会话
        :param product: 筛选id以及is_datete_prod是否为None
        :return 成功后返回product
        """
        product = db.query(Product).filter(Product.id == product_id,Product.is_delete_prod == 0).first()
        if not product:
            return None
        Product.is_delete_prod = 1
        Product.delete_time = dt.now()
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def deleted_list(db:Session,page:int = 1,size:int = 10,name: str |None = None) ->dict:
        """
        分页查询【回收站】的商品（只查已经软删除的商品）
        :param db: 数据库会话
        :param page: 当前第几页,默认第1页
        :param size: 每页显示多少条,默认10条
        :param name: 可选的商品过滤
        :return: 分页数据（列表+页码+总数+总页数）
        """
        skip = (page-1)*size
        query = db.query(Product).filter(Product.is_delete_prod == 1)
        if name is not None:
            name = name.strip()
            if name:
                query = query.filter(Product.name.like(f"%{name}%"))
        product_list = query.offset(skip).limit(size).all()
        total = query.count()
        total_pages = (total+size-1)//size
        return {
            "list" : product_list, # 当前订单数据
            "page" : page, # 当前页码
            "size" : size, # 每页多少条
            "total" : total, # 回收站总条数
            "total_pages" : total_pages # 一共多少页
        }
    
    @staticmethod
    def restore_product(db:Session,product_id:int) ->Product|None:
        """
        恢复已删除的数据
        :param db: 数据会话
        :param product: 筛选id
        :param product.is_delete: 恢复数据,取消删除标记
        :param delete_time: 清除时间
        return 如果有返回product如果没有返回None
        """
        product = db.query(Product).filter(Product.id == product_id,Product.is_delete_prod == 1).first()
        if not product:
            return None
        product.is_delete_prod = 0
        product.delete_time = None
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def hard_product(db:Session,product_id:int) ->Product|None:
        """
        永久删除数据(不能恢复)
        :param db: 数据库会话
        :param product: 筛选id
        :return: 等于则返回product,不等于则返回None空
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        db.delete(product)
        db.commit()
        return product
    
    @staticmethod
    def query_name_product(db:Session,name:str) ->Product|None:
        """
        根据商品名称查重（仅未删除数据）
        """
        return db.query(Product).filter(Product.name == name,Product.is_delete_prod == 0).first()