import flet as ft
from sqlalchemy import cast, or_, select
from sqlalchemy.types import String

from core.db import Session
from models.items import Category, Item, Producer, Unit, Vendor

DEFAULT_IMAGE_PATH = (
    "/Users/arsenijkarpov/Documents/Колледж/4 курс/scratch/demo/src/assets/ph.jpg"
)


class ItemsView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.sort_in_stock_desc = None
        self.page = page
        self.route = "/items"

        name = self.page.client_storage.get("name")
        role = self.page.client_storage.get("role")
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(role, size=18),
                    ft.Row(
                        controls=[
                            ft.Text(name, size=18),
                            ft.Button(
                                "Выйти",
                                on_click=lambda e: e.page.go("/login"),
                                bgcolor="#00FA9A",
                            ),
                        ]
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor="#BDBDBD",
            padding=5,
        )

        title = ft.Text("Список товаров", size=20)

        self.search_field = ft.TextField(
            label="Поиск", on_change=lambda _: (self.reload_table(), self.update())
        )
        self.sort_in_stock_btn = ft.Button(
            "Кол-во на складе", on_click=lambda _: self.sort_in_stock()
        )
        with Session() as session:
            stmt = select(Vendor)
            vendors = session.scalars(stmt).all()
            self.vendor_dropdown = ft.Dropdown(
                label="Поставщик",
                options=[
                    ft.DropdownOption(text="Все поставщики", key=None),
                    *(ft.DropdownOption(text=v.name, key=v.id) for v in vendors),
                ],
                on_change=lambda _: (self.reload_table(), self.update()),
                value=None,
            )
        filters_row = ft.Row(
            controls=[self.vendor_dropdown, self.sort_in_stock_btn, self.search_field]
        )

        self.item_list = ft.Column(scroll=True, expand=True)
        self.reload_table()

        self.controls = [header, title, filters_row, self.item_list]

    def reload_table(self):
        self.item_list.controls.clear()
        search_str = self.search_field.value
        with Session() as session:
            stmt = select(Item)
            if search_str:
                stmt = (
                    stmt.join(Item.category)
                    .join(Item.producer)
                    .join(Item.vendor)
                    .join(Item.unit)
                    .where(
                        or_(
                            Item.name.contains(search_str),
                            Item.description.contains(search_str),
                            Item.article.contains(search_str),
                            Category.name.contains(search_str),
                            Producer.name.contains(search_str),
                            Vendor.name.contains(search_str),
                            Unit.name.contains(search_str),
                            cast(Item.in_stock, String).contains(search_str),
                            cast(Item.price, String).contains(search_str),
                            cast(Item.discount, String).contains(search_str),
                        )
                    )
                )

            if self.vendor_dropdown.value:
                stmt = stmt.where(Item.vendor_id == int(self.vendor_dropdown.value))

            if self.sort_in_stock_desc is True:
                stmt = stmt.order_by(Item.in_stock.desc())
            elif self.sort_in_stock_desc is False:
                stmt = stmt.order_by(Item.in_stock.asc())

            items = session.scalars(stmt)
            for item in items:
                img_path = (
                    item.picture_path if item.picture_path else DEFAULT_IMAGE_PATH
                )
                img = ft.Image(width=200, height=200, src=img_path)
                first_line = ft.Text(
                    f"{item.category.name} | {item.name}",
                    weight=ft.FontWeight.BOLD,
                )
                other = ft.Text(
                    f"Описание товара: {item.description}\n"
                    f"Производитель: {item.producer.name}\n"
                    f"Поставщик: {item.vendor.name}\n"
                    f"Ед. изм.: {item.unit.name}\n"
                    f"На складе: {item.in_stock}"
                )
                original_price = item.price
                discounted_price = original_price * (1 - item.discount / 100)
                if item.discount > 0:
                    price_text = ft.Row(
                        controls=[
                            ft.Text(
                                f"{original_price:.2f}",
                                color=ft.Colors.RED,
                                style=ft.TextStyle(
                                    decoration=ft.TextDecoration.LINE_THROUGH
                                ),
                            ),
                            ft.Text(" -> ", size=16),
                            ft.Text(
                                f"{discounted_price:.2f}", weight=ft.FontWeight.BOLD
                            ),
                        ],
                        spacing=2,
                    )
                else:
                    price_text = ft.Text(f"Цена: {original_price:.2f}")

                text_column = ft.Column(
                    controls=[first_line, other, ft.Text("Цена:"), price_text],
                    spacing=4,
                    expand=True,
                )

                text = ft.Container(
                    content=text_column,
                    border=ft.border.all(1, "#000000"),
                    # height=200,
                    alignment=ft.Alignment(0, 0),
                    border_radius=5,
                    padding=5,
                    expand=True,
                )
                discount = ft.Container(
                    content=ft.Text(f"{item.discount}%"),
                    border=ft.border.all(1, "#000000"),
                    height=200,
                    width=200,
                    alignment=ft.Alignment(0, 0),
                    border_radius=5,
                )
                ctrl = ft.Container(
                    content=ft.Row(
                        controls=[img, text, discount],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.all(1, "#000000"),
                    border_radius=5,
                    padding=ft.padding.all(5),
                )
                if item.discount >= 15:
                    ctrl.bgcolor = "#2E8B57"
                elif item.in_stock <= 0:
                    ctrl.bgcolor = ft.Colors.BLUE
                self.item_list.controls.append(ctrl)

    def sort_in_stock(self):
        if self.sort_in_stock_btn.icon is None:
            self.sort_in_stock_btn.icon = ft.Icons.ARROW_DOWNWARD
            self.sort_in_stock_desc = True
        elif self.sort_in_stock_btn.icon is ft.Icons.ARROW_DOWNWARD:
            self.sort_in_stock_btn.icon = ft.Icons.ARROW_UPWARD
            self.sort_in_stock_desc = False
        else:
            self.sort_in_stock_btn.icon = None
            self.sort_in_stock_desc = None
        self.reload_table()
        self.update()
