#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend import __description__, __title__, __version__
from backend.constants import BackendConf
from backend.routes import echo

PREFIX = "/v1"


def create_app() -> FastAPI:
    app = FastAPI(
        title=__title__,
        description=__description__,
        version=__version__,
    )

    @app.get("/")
    async def landing():
        """Redirect to root of latest version of the API"""
        return RedirectResponse(f"{PREFIX}/", status_code=308)

    api = FastAPI(
        title=__title__,
        description=__description__,
        version=__version__,
        docs_url="/",
        openapi_tags=[
            {
                "name": "all",
                "description": "all APIs",
            },
        ],
        contact={
            "name": "Kiwix/openZIM Team",
            "url": "https://www.kiwix.org/en/contact/",
            "email": "contact+offspot_metrics@kiwix.org",
        },
        license_info={
            "name": "GNU General Public License v3.0",
            "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
        },
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=BackendConf.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.include_router(router=echo.router)

    app.mount(PREFIX, api)

    return app
