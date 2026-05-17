import typer
from auth_app.db import sqlalchemy
from auth_app.main import create_engine_

from cli import admin, init_service_accounts, user

app = typer.Typer(name="cli")

sqlalchemy.engine = create_engine_()

app.add_typer(admin.router, name="admin")
app.add_typer(init_service_accounts.router, name="service")
app.add_typer(user.router, name="user")

if __name__ == "__main__":
    app()
