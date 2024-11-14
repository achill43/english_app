from injector import Inject
from pydantic import BaseModel
from pydiator_core.interfaces import BaseResponse
from pydiator_core.mediatr import BaseRequest
from pydiator_core.mediatr_container import BaseHandler
from repositories.products_repository import ProductRepository
from schemas.products import Product


class GetProductsListRequest(BaseModel, BaseRequest):
    pass


class GetProductsListResponse(BaseModel, BaseResponse):
    products: list[Product]


class GetProductsListHandler(BaseHandler):
    def __init__(self, product_repository: Inject[ProductRepository]):
        self.product_repository = product_repository

    async def handle(self, req: GetProductsListRequest) -> GetProductsListResponse:
        products = await self.product_repository.get_list()
        return GetProductsListResponse(
            products=[Product.from_orm(product) for product in products]
        )
