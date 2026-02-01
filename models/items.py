import datetime as dt
from typing import Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(255), unique=True)


class Producer(Base):
    __tablename__ = "producers"

    name: Mapped[str] = mapped_column(String(255), unique=True)


class Vendor(Base):
    __tablename__ = "vendors"

    name: Mapped[str] = mapped_column(String(255), unique=True)


class Unit(Base):
    __tablename__ = "units"

    name: Mapped[str] = mapped_column(String(50), unique=True)


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), unique=True)


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    name: Mapped[str] = mapped_column(String(100), unique=True)


class PickupPoint(Base):
    __tablename__ = "pickup_points"

    address: Mapped[str] = mapped_column(TEXT())


class User(Base):
    __tablename__ = "users"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    name: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    role: Mapped["Role"] = relationship()
    orders: Mapped[list["Order"]] = relationship(back_populates="client")


class Item(Base):
    __tablename__ = "items"

    picture_path: Mapped[Optional[str]] = mapped_column(TEXT())
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(TEXT())
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    producer_id: Mapped[int] = mapped_column(ForeignKey("producers.id"))
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"))
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"))
    category: Mapped["Category"] = relationship()
    producer: Mapped["Producer"] = relationship()
    vendor: Mapped["Vendor"] = relationship()
    unit: Mapped["Unit"] = relationship()
    price: Mapped[float]
    in_stock: Mapped[int]
    discount: Mapped[int]
    article: Mapped[str] = mapped_column(String(255), unique=True)

    orders: Mapped[list["OrderItem"]] = relationship(back_populates="item")


class Order(Base):
    __tablename__ = "orders"

    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("order_statuses.id"))
    pickup_point_id: Mapped[int] = mapped_column(ForeignKey("pickup_points.id"))
    client: Mapped["User"] = relationship(back_populates="orders")
    status: Mapped["OrderStatus"] = relationship()
    pickup_point: Mapped["PickupPoint"] = relationship()
    order_date: Mapped[dt.datetime] = mapped_column(default=func.now())
    delivery_date: Mapped[Optional[dt.datetime]]
    pickup_code: Mapped[str] = mapped_column(String(255))

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    quantity: Mapped[int]
    price: Mapped[float]
    order: Mapped["Order"] = relationship(back_populates="items")
    item: Mapped["Item"] = relationship(back_populates="orders")
