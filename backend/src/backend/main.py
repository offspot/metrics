#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
from asyncio import create_task, sleep

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend import __description__, __title__, __version__
from backend.business.log_converter import LogConverter
from backend.business.period import Period
from backend.business.processor import Processor
from backend.constants import BackendConf
from backend.filebeat import FileBeatRunner
from backend.routes import aggregations, kpis

PREFIX = "/v1"

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s: %(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=__title__,
        description=__description__,
        version=__version__,
    )

    converter = LogConverter()
    converter.parse_package_configuration_from_file()
    filebeat = FileBeatRunner(converter=converter)
    processor = Processor()
    processor.startup(now=Period.now())

    @app.on_event("startup")
    async def app_startup():  # pyright: ignore[reportUnusedFunction]
        """Start background tasks"""
        create_task(filebeat.run(processor))
        create_task(ticker())

    async def ticker():
        """Start a processor tick every minute"""
        while True:
            await sleep(60)
            logger.debug("Processing a clock tick")
            processor.process_tick(now=Period.now())

    @app.get("/")
    async def landing() -> RedirectResponse:  # pyright: ignore[reportUnusedFunction]
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

    api.include_router(router=aggregations.router)
    api.include_router(router=kpis.router)

    app.mount(PREFIX, api)

    return app
