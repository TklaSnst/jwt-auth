from fastapi import APIRouter

router = APIRouter(
    prefix="/basic",
    tags=["basic-endpoints"]
)

@router.get("/hello")
async def hello():
    return "hello"