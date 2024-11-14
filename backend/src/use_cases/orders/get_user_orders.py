from decimal import Decimal

from fastapi import Query
from injector import Inject
from pydantic import BaseModel
from pydiator_core.interfaces import BaseResponse
from pydiator_core.mediatr import BaseRequest
from pydiator_core.mediatr_container import BaseHandler
from repositories.order_repository import OrderRepository
from request_context import RequestContextProvider
from schemas.orders import Order, OrderFilter, OrderItem, Payment


class GetUserOrdersRequest(OrderFilter, BaseRequest):
    page: int = Query(1, ge=1, description="Page number")
    page_size: int = Query(1, ge=1, le=500, description="Page size")


class GetUserOrdersResponse(BaseModel, BaseResponse):
    orders: list[Order]


class GetUserOrdersHandler(BaseHandler):
    def __init__(
        self,
        context: Inject[RequestContextProvider],
        order_repository: Inject[OrderRepository],
    ):
        self.contex = context
        self.order_repository = order_repository

    async def handle(self, req: GetUserOrdersRequest) -> GetUserOrdersResponse:
        user = self.contex.get_user()
        filters = OrderFilter(**req.dict())
        orders = await self.order_repository.get_user_orders(
            user_id=user["user_id"],
            page=req.page,
            page_size=req.page_size,
            filters=filters,
        )
        user_orders = list()
        for order in orders:
            user_orders.append(
                Order(
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
            )
        return GetUserOrdersResponse(orders=user_orders)
