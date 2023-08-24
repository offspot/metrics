import logging
import os
from asyncio import create_task, sleep

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

    # Boolean stoping background processing of logs + indicators / kpis update / cleanup
    # Useful mostly for local development purpose when we do not want to generate new
    # events regularly and hence do not want to cleanup DB from simulation results
    # The environment variable must hence be explicitely set to False (case-insensitive)
    # all other values will start the processing.
    run_processing = not (os.getenv("RUN_PROCESSING", "False").lower() == "false")

    if run_processing:
        logger.info("Starting processing")
        converter = LogConverter()
        converter.parse_package_configuration_from_file()
        filebeat = FileBeatRunner(converter=converter)
        processor = Processor()
        processor.startup(current_period=Period.now())
    else:
        logger.warning("Processing is disabled")

    background_tasks = set()

    @app.on_event("startup")
    async def app_startup():  # pyright: ignore[reportUnusedFunction]
        """Start background tasks"""
        if run_processing and filebeat and processor:
            filebeat_task = create_task(filebeat.run(processor))
            background_tasks.add(filebeat_task)
            filebeat_task.add_done_callback(background_tasks.discard)

            ticker_task = create_task(ticker())
            background_tasks.add(ticker_task)
            ticker_task.add_done_callback(background_tasks.discard)

    async def ticker():
        """Start a processor tick every minute"""
        while True:
            await sleep(60)
            if not processor:
                system_exit = SystemExit("Processor is not set")
                system_exit.code = 1
                raise system_exit
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
