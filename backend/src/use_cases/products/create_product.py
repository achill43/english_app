from injector import Inject
from models.products import ProductSQL
from pydantic import BaseModel
from pydiator_core.interfaces import BaseResponse
from pydiator_core.mediatr import BaseRequest
from pydiator_core.mediatr_container import BaseHandler
from repositories.products_repository import ProductRepository
from schemas.products import Product, ProductCreate


class CreateProductRequest(ProductCreate, BaseRequest):
    pass


class CreateProductResponse(BaseModel, BaseResponse):
    product: Product


class CreateProductHandler(BaseHandler):
    def __init__(self, product_repository: Inject[ProductRepository]):
        self.product_repository = product_repository

    async def handle(self, req: CreateProductRequest) -> CreateProductResponse:
        product = await self.product_repository.create(
            ProductSQL(name=req.name, price=req.price)
        )
        return CreateProductResponse(product=Product.from_orm(product))
