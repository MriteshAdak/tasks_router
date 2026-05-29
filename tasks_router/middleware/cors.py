from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def register_cors_middleware(app: FastAPI) -> None:
    """
    Registers CORS middleware to the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance to which the CORS middleware will be added.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        # allow_credentials=True,
    )