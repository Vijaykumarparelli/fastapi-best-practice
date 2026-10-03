from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import Theme, get_scalar_api_reference

from config.db import create_all_tables
from routers.auth_router import router as auth_router
from routers.partner_router import router as partner_router
from routers.shipment_router import router as shipment_router


@asynccontextmanager
async def lifespan(app):
    await create_all_tables()
    yield


tags_metadata = [
    {"name": "auth", "description": "User registration, login, JWT tokens and logout."},
    {"name": "partner", "description": "Delivery partner registration, login, JWT tokens and logout."},
    {"name": "shipment", "description": "Create and list shipments for the logged-in user."},
]

app = FastAPI(
    title="FastAPI Best Practice API",
    summary="Production-style FastAPI project structure with SQLModel, async MySQL, Alembic and JWT auth.",
    description=(
        "Reference FastAPI application showing a layered **router → controller → model** "
        "architecture, async MySQL with SQLModel, Alembic migrations, JWT authentication "
        "and logout via a Redis token blacklist.\n\n"
        "Source: [github.com/Vijaykumarparelli/fastapi-best-practice]"
        "(https://github.com/Vijaykumarparelli/fastapi-best-practice)"
    ),
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)
app.include_router(auth_router)
app.include_router(shipment_router)
app.include_router(partner_router)


@app.get("/scalar", response_class=HTMLResponse, include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Scalar API",
        theme=Theme.BLUE_PLANET,
    )
