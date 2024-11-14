from decimal import Decimal

from fastapi import Query
from fastapi.concurrency import run_in_threadpool
from fastapi.templating import Jinja2Templates
from injector import Inject
from pydantic import BaseModel
from pydiator_core.interfaces import BaseResponse
from pydiator_core.mediatr import BaseRequest
from pydiator_core.mediatr_container import BaseHandler
from repositories.order_repository import OrderRepository
from repositories.user_repository import UserRepository
from request_context import RequestContextProvider
from schemas.orders import Order, OrderItem, Payment
from sqlalchemy.sql.functions import user


class GenerateCheckRequest(BaseModel, BaseRequest):
    id: int = Query(1, ge=1, description="Order ID")


class GenerateCheckResponse(BaseModel, BaseResponse):
    order: Order
    html_content: str


class GenerateCheckHandler(BaseHandler):
    def __init__(
        self,
        context: Inject[RequestContextProvider],
        order_repository: Inject[OrderRepository],
        user_repository: Inject[UserRepository],
    ):
        self.contex = context
        self._templates = Jinja2Templates(directory="templates")
        self.order_repository = order_repository
        self.user_repository = user_repository

    async def handle(self, req: GenerateCheckRequest) -> GenerateCheckResponse:
        order = await self.order_repository.get_by_id(order_id=req.id)
        order_obj = Order(
            id=order.id,
            products=[
                OrderItem(
                    id=item.id,
                    name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                    total=Decimal(item.quantity * item.product.price),
                )
                for item in order.items
            ],
            payment=Payment.from_orm(order.payment),
            total=order.total,
            rest=order.rest,
            created_at=order.created_at.date(),
        )
        user = await self.user_repository.get_by_id(user_id=order.user_id)
        template = self._templates.get_template("check.html")
        data = {"order": order_obj, "user": user}
        html_content = await run_in_threadpool(template.render, data)
        return GenerateCheckResponse(order=order_obj, html_content=html_content)
