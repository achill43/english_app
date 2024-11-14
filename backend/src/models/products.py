from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List

import models
from db import Base
from sqlalchemy import DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class ProductSQL(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[Decimal] = mapped_column(DECIMAL(20, 2))

    items: Mapped[List["OrderItemSQL"]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name}, price={self.price}>"

    def __str__(self) -> str:
        return self.__repr__()


class OrderSQL(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total: Mapped[Decimal] = mapped_column(DECIMAL(20, 2))
    rest: Mapped[Decimal] = mapped_column(DECIMAL(20, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["models.users.UserSQL"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItemSQL"]] = relationship(back_populates="order")
    payment: Mapped["PaymentSQL"] = relationship(back_populates="order")


class PaymentType(Enum):
    cash = "cash"
    cashless = "cashless"


class PaymentSQL(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    type: Mapped[PaymentType] = mapped_column()
    amount: Mapped[Decimal] = mapped_column(DECIMAL(20, 2))

    order: Mapped["OrderSQL"] = relationship(back_populates="payment")


class OrderItemSQL(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()

    order: Mapped["OrderSQL"] = relationship(back_populates="items")
    product: Mapped["ProductSQL"] = relationship(back_populates="items")
