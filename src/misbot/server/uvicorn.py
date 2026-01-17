import uvicorn
import fastapi
import logging


def initialize_unvicorn_fastapi_server(app: fastapi.FastAPI) -> uvicorn.Server:
    uvicorn_config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8080,
        loop="asyncio",
        lifespan="on",
        log_level=logging.INFO,
    )
    return uvicorn.Server(uvicorn_config)
