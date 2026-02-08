import flet as ft
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.db import Session
from models.items import User


class LoginView(ft.View):
    def __init__(self, page: ft.Page, go_to_route):
        super().__init__()
        self.page = page
        self.route = "/login"

        title = ft.Text("Вход", size=20)
        self.login_field = ft.TextField(label="Логин")
        self.password_field = ft.TextField(label="Пароль", password=True)
        submit_btn = ft.Button("Войти", on_click=self.submit, bgcolor="#00FA9A")
        guest_btn = ft.Button("Войти как Гость", on_click=self.guest, bgcolor="#00FA9A")

        self.controls = [
            ft.Column(
                controls=[
                    title,
                    self.login_field,
                    self.password_field,
                    ft.Column(
                        controls=[submit_btn, guest_btn],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        width=300,
                    ),
                ],
                width=300,
            )
        ]
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.go_to_route = go_to_route

    def submit(self, e):
        login = self.login_field.value
        password = self.password_field.value
        if not login:
            self.login_field.error_text = "Введите пароль"
        else:
            self.login_field.error_text = ""
        if not password:
            self.password_field.error_text = "Введите пароль"
        else:
            self.password_field.error_text = ""
        self.update()
        if not login or not password:
            return

        with Session() as session:
            stmt = (
                select(User)
                .where(User.password == password, User.login == login)
                .options(selectinload(User.role))
            )
            user = session.scalar(stmt)
            self.page.client_storage.set("role", user.role.name)
            self.page.client_storage.set("name", user.name)
            if not user:
                return

        self.page.go(self.go_to_route)

    def guest(self, e):
        self.page.client_storage.set("role", "Гость")
        self.page.client_storage.set("name", "Гость")
        self.page.go(self.go_to_route)
