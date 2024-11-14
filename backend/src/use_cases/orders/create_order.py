from decimal import Decimal
from typing import cast

from injector import Inject
from models.products import OrderItemSQL, OrderSQL, PaymentSQL, ProductSQL
from pydantic import BaseModel
from pydiator_core.interfaces import BaseResponse
from pydiator_core.mediatr import BaseRequest
from pydiator_core.mediatr_container import BaseHandler
from repositories.order_item_repository import OrderItemRepository
from repositories.order_repository import OrderRepository
from repositories.payment_repository import PaymentRepository
from repositories.products_repository import ProductRepository
from request_context import RequestContextProvider
from schemas.orders import (Order, OrderCreate, OrderItem, OrderItemCreate,
                            Payment)


class CreateOrderRequest(OrderCreate, BaseRequest):
    pass


class CreateOrderResponse(BaseModel, BaseResponse):
    order: Order


class CreateOrderHandler(BaseHandler):
    def __init__(
        self,
        context: Inject[RequestContextProvider],
        order_repository: Inject[OrderRepository],
        order_item_repository: Inject[OrderItemRepository],
        payment_repository: Inject[PaymentRepository],
        product_repository: Inject[ProductRepository],
    ):
        self.contex = context
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository
        self.payment_repository = payment_repository
        self.product_repository = product_repository

    async def handle(self, req: CreateOrderRequest) -> CreateOrderResponse:
        user = self.contex.get_user()
        current_amount = Decimal(0.0)
        order_items = list()
        for product in req.products:
            order_items.append(
                OrderItemCreate(
                    product_id=product.product_id, quantity=product.quantity
                )
            )
            product_sql = cast(
                ProductSQL,
                await self.product_repository.get_by_id(product_id=product.product_id),
            )
            product_amount = product_sql.price * product.quantity
            current_amount = current_amount + Decimal(product_amount)
        order = await self.order_repository.create(
            OrderSQL(
                user_id=user["user_id"],
                total=req.total,
                rest=Decimal(req.total - current_amount),
            )
        )
        await self.payment_repository.create(
            PaymentSQL(order_id=order.id, type=req.payment.type, amount=current_amount)
        )
        order_items_sql = [
            OrderItemSQL(
                order_id=order.id, product_id=item.product_id, quantity=item.quantity
            )
            for item in order_items
        ]
        await self.order_item_repository.bulk_create(order_items=order_items_sql)
        order = await self.order_repository.get_by_id(order_id=order.id)
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
        return CreateOrderResponse(order=order_obj)
