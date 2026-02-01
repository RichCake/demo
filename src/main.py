import flet as ft

from src.items import ItemsView
from src.login import LoginView


def main(page: ft.Page):
    page.title = "Товары"

    def on_route_change(route):
        page.views.clear()
        if page.route == "/login":
            page.views.append(LoginView(page, "/items"))
        elif page.route == "/items":
            page.views.append(ItemsView(page))
        page.update()

    page.on_route_change = on_route_change
    page.go("/login")
    page.update()


ft.app(main)
