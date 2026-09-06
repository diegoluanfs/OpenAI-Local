from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["web"])
WEB_ROOT = Path(__file__).resolve().parents[3] / "web"


@router.get("/", include_in_schema=False)
async def web_app() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")
