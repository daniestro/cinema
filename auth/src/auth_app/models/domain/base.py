from sqlalchemy import Column
from sqlmodel import Field, text
from sqlmodel.sql.sqltypes import GUID


def get_uuid_field():
    return Field(
        sa_column=Column(
            GUID,
            server_default=text("gen_random_uuid()"),
            primary_key=True,
            index=True,
            nullable=False,
        ),
    )
