import tomllib
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend import __about__
from backend.constants import BackendConf
from backend.routes import echo

PREFIX = "/v1"


def create_app() -> FastAPI:
    toml_content = tomllib.loads(
        (Path(__file__).parent.parent.parent / Path("pyproject.toml")).read_text()
    )

    app = FastAPI(
        title=toml_content["project"]["name"],
        description=toml_content["project"]["description"],
        version=__about__.__version__,
    )

    @app.get("/")
    async def landing() -> RedirectResponse:  # pyright: ignore[reportUnusedFunction]
        """Redirect to root of latest version of the API"""
        return RedirectResponse(f"{PREFIX}/", status_code=308)

    api = FastAPI(
        title=toml_content["project"]["name"],
        description=toml_content["project"]["description"],
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

    api.include_router(router=echo.router)

    app.mount(PREFIX, api)

    return app
