import logging
from asyncio import create_task

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from offspot_metrics_backend import __about__
from offspot_metrics_backend.business.log_converter import LogConverter
from offspot_metrics_backend.constants import BackendConf
from offspot_metrics_backend.filebeat import FileBeatRunner
from offspot_metrics_backend.routes import aggregations, kpis

PREFIX = "/v1"

# fix this, this is not the same log as uvicorn ...
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s: %(levelname)s] %(message)s"
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=__about__.__api_title__,
        description=__about__.__api_description__,
        version=__about__.__version__,
    )

    converter = LogConverter()
    filebeat = FileBeatRunner(converter=converter)

    @app.on_event("startup")
    async def app_startup():  # pyright: ignore[reportUnusedFunction]
        create_task(filebeat.run())

    @app.get("/")
    async def landing() -> RedirectResponse:  # pyright: ignore[reportUnusedFunction]
        """Redirect to root of latest version of the API"""
        return RedirectResponse(f"/{__about__.__api_version__}/", status_code=308)

    api = FastAPI(
        title=__about__.__api_title__,
        description=__about__.__api_description__,
        version=__about__.__version__,
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

    app.mount(f"/{__about__.__api_version__}", api)

    return app
