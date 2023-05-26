from fastapi import APIRouter

router = APIRouter(
    prefix="/echo",
    tags=["all"],
)


@router.get(
    "",
    status_code=200,
    responses={
        200: {
            "description": "Display ECHO",
        },
    },
)
async def echo():
    return "ECHO"
