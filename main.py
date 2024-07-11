from loguru import logger

from fastapi import FastAPI
import MAPE.mape as ControlLoop
import app.handler.handler as Handler

from starlette.responses import RedirectResponse


logger.add("./logs/file_app.log", rotation="1 MB")


app = FastAPI(
    title="FastAPI",
    description="",
    version="0.75.2",
)

@app.get("/", tags=["Home"])
async def redirect():
    response = RedirectResponse(url='/docs')
    return response

app.include_router(
    Handler.router,
    prefix="/client",
    tags=["Client Route"]
)

app.include_router(
    ControlLoop.mape_router,
    prefix="/mape",
    tags=["MAPE Route"]
)
