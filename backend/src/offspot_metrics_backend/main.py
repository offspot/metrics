import functools
import sys
from asyncio import Task, create_task, sleep
from contextlib import asynccontextmanager
from http import HTTPStatus
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from offspot_metrics_backend import __about__
from offspot_metrics_backend.business.caddy_log_converter import CaddyLogConverter
from offspot_metrics_backend.business.log_watcher import LogWatcher, NewLineEvent
from offspot_metrics_backend.business.processor import INACTIVITY_PERIOD, Processor
from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig
from offspot_metrics_backend.constants import BackendConf, logger
from offspot_metrics_backend.db.initializer import Initializer
from offspot_metrics_backend.routes import aggregations, kpis

PREFIX = "/v1"


class Main:
    def __init__(self) -> None:
        self.log_watcher = None
        if BackendConf.processing_enabled:
            self.log_watcher = LogWatcher(
                watched_folder=BackendConf.reverse_proxy_logs_location,
                handler=self.handle_log_event,
                data_folder=BackendConf.logwatcher_data_folder,
            )
        self.background_tasks = set[Task[Any]]()

    @asynccontextmanager
    async def lifespan(self, _: FastAPI):
        # Startup
        logger.debug(f"Database URL: {BackendConf.database_url}")
        Initializer.upgrade_db_schema()
        if BackendConf.processing_enabled:
            logger.info("Starting processing")
            self.processor = Processor()
            self.config = ReverseProxyConfig()
            self.config.parse_configuration()
            self.converter = CaddyLogConverter(self.config)
            self.processor.startup()

            log_watcher_task = create_task(self.start_watcher())
            self.background_tasks.add(log_watcher_task)
            log_watcher_task.add_done_callback(
                functools.partial(self.task_stopped, "Log Watcher")
            )

            check_for_inactivity_task = create_task(self.check_for_inactivity())
            self.background_tasks.add(check_for_inactivity_task)
            check_for_inactivity_task.add_done_callback(
                functools.partial(self.task_stopped, "Check for inactivity")
            )
        else:
            logger.warning("Processing is disabled")
        # Startup complete
        yield
        # Shutdown
        if self.log_watcher:
            self.log_watcher.stop()

    def task_stopped(self, task_name: str, task: Task[Any]) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        self.background_tasks.discard(task)
        if exc:
            logger.error(f"{task_name} has stopped anormally", exc_info=exc)
            sys.exit(1)

    async def start_watcher(self):
        """Start the log watcher as a coroutine"""
        if not self.log_watcher:
            raise ValueError("Log watcher has not been initialized")
        await self.log_watcher.run_async()

    async def check_for_inactivity(self):
        """Check for inactivity every 10 seconds

        If the system did not received any log since more than 10 seconds and there has
        been more than 1 minute since the last processing cycle, a new one will be
        started
        """
        while True:
            await sleep(INACTIVITY_PERIOD)
            try:
                self.processor.check_for_inactivity()
            except Exception as exc:
                logger.debug(
                    "Exception occured in check for inactivity tick", exc_info=exc
                )

    def handle_log_event(self, event: NewLineEvent):
        """Handle one log line

        We first transform the log line into a list of input events, and then feed it to
        the processing logic.
        """
        logger.debug(f"Log watcher sent: {event.line_content}")
        try:
            result = self.converter.process(event.line_content)
            self.processor.process_inputs(result=result)
        except Exception as exc:
            logger.debug("Error log event", exc_info=exc)

    def create_app(self) -> FastAPI:
        self.app = FastAPI(
            title=__about__.__api_title__,
            description=__about__.__api_description__,
            version=__about__.__version__,
            lifespan=self.lifespan,
        )

        @self.app.get("/api")
        async def landing() -> RedirectResponse:  # pyright: ignore
            """Redirect to root of latest version of the API"""
            return RedirectResponse(
                f"/api/{__about__.__api_version__}/",
                status_code=HTTPStatus.TEMPORARY_REDIRECT,
            )

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

        self.app.mount(f"/api/{__about__.__api_version__}", api)

        class ServeVueUiFromRoot(BaseHTTPMiddleware):
            """Custom middleware to serve the Vue.JS application

            We need a bit of black magic to:
            - serve the Vue.JS UI from "/"
            - but still keep the API on "/api"
            - and support Vue.JS routes like "/home"
            - and still return 404 when the UI is requesting a file which does not exits
            """

            ui_location = Path()

            async def dispatch(
                self, request: Request, call_next: RequestResponseEndpoint
            ):
                path = request.url.path

                # API is served normally
                if path.startswith("/api"):
                    response = await call_next(request)
                    return response

                # Serve index.html on root
                if path == "/":
                    return FileResponse(BackendConf.ui_location.joinpath("index.html"))

                local_path = BackendConf.ui_location.joinpath(path[1:])

                # If there is no dot, then we are probably serving a Vue.JS internal
                # route, so let's serve Vue.JS app
                if "." not in local_path.name:
                    return FileResponse(BackendConf.ui_location.joinpath("index.html"))

                # If the path exists and is a file, serve it
                if local_path.exists() and local_path.is_file():
                    return FileResponse(local_path)

                # Otherwise continue to next handler (which is probably a 404)
                response = await call_next(request)
                return response

        # Apply the custom middleware
        self.app.add_middleware(ServeVueUiFromRoot)

        return self.app
