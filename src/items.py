import flet as ft
from sqlalchemy import select

from core.db import Session
from models.items import Item

DEFAULT_IMAGE_PATH = (
    "/Users/arsenijkarpov/Documents/Колледж/4 курс/scratch/demo/src/assets/ph.jpg"
)


class ItemsView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
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
                            ft.Button("Выйти", on_click=lambda e: e.page.go("/login")),
                        ]
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor="#BDBDBD",
            padding=5,
        )

        title = ft.Text("Список товаров", size=20)

        item_list = ft.Column(scroll=True, expand=True)

        with Session() as session:
            stmt = select(Item)
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
                item_list.controls.append(ctrl)

        self.controls = [header, title, item_list]
