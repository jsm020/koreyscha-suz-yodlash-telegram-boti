import uvicorn
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.factory import app as admin_factory
from fastapi_admin.resources import Model
from fastapi_admin.widgets import displays, inputs
from starlette.requests import Request
from .models import Word
from .database import engine, SessionLocal
import sqlalchemy

# FastAPI-Admin uchun sozlamalar
async def on_startup():
    await admin_app.configure(
        logo_url="https://fastapi-admin.github.io/img/logo.png",
        template_folders=[],
        providers=[
            UsernamePasswordProvider(
                admin_model=None,  # Oddiy autentifikatsiya uchun
                login_logo_url="https://fastapi-admin.github.io/img/logo.png",
            )
        ],
        resources=[
            Model(Word, 
                icon="fa fa-database",
                label="Words",
                display_fields=[displays.Field("id"), displays.Field("word"), displays.Field("translation")],
                inputs=[inputs.Text("word"), inputs.Text("translation")],
            )
        ],
        engine=engine,
        session_maker=SessionLocal,
    )

# FastAPI-Admin app
admin = admin_factory()
admin.on_event("startup")(on_startup)
