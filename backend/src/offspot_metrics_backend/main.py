import logging
import sys
from asyncio import Task, create_task, sleep
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from offspot_metrics_backend import __about__
from offspot_metrics_backend.business.log_converter import LogConverter
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.business.processor import Processor
from offspot_metrics_backend.constants import BackendConf
from offspot_metrics_backend.filebeat import FileBeatRunner
from offspot_metrics_backend.routes import aggregations, kpis

PREFIX = "/v1"
TICK_PERIOD = (
    60  # tick period in seconds, changing this need a detailed impact analysis
)

# - fix this, this is not the same log format as uvicorn logs but are mixed in the same
#  STDOUT...
# - read debug level from environment variable
logging.basicConfig(
    level=logging.DEBUG, format="[%(asctime)s: %(levelname)s] %(message)s"
)


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=__about__.__api_title__,
        description=__about__.__api_description__,
        version=__about__.__version__,
    )

    if not BackendConf.filebeat_present:
        logger.warning(
            f"filebeat process not found at {BackendConf.filebeat_process_location}"
        )

    if BackendConf.processing_disabled or not BackendConf.filebeat_present:
        logger.warning("Processing is disabled")
        converter = filebeat = processor = None
    else:
        logger.info("Starting processing")
        converter = LogConverter()
        filebeat = FileBeatRunner(converter=converter)
        processor = Processor()
        processor.startup(current_period=Period.now())

    background_tasks = set[Task[Any]]()

    @app.on_event("startup")
    async def app_startup():  # pyright: ignore[reportUnusedFunction]
        """Start background tasks"""
        if not BackendConf.processing_disabled and filebeat and processor:
            filebeat_task = create_task(filebeat.run(processor))
            background_tasks.add(filebeat_task)
            filebeat_task.add_done_callback(background_tasks.discard)

            ticker_task = create_task(ticker())
            background_tasks.add(ticker_task)
            ticker_task.add_done_callback(background_tasks.discard)

    async def ticker():
        """Start a processor tick every minute"""
        while True:
            await sleep(TICK_PERIOD)
            if not processor:
                # This should never happen, but better safe than sorry
                sys.exit("Processor is not set")
            logger.debug("Processing a clock tick")
            processor.process_tick(tick_period=Period.now())

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
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.include_router(router=aggregations.router)
    api.include_router(router=kpis.router)

    app.mount(f"/{__about__.__api_version__}", api)

    return app
