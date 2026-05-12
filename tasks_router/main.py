from fastapi import FastAPI

from tasks_router.routers.task_router import router as task_router

router = FastAPI(redirect_slashes=False)

router.include_router(task_router)