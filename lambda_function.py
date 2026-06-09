from mangum import Mangum

from tasks_router.main import app

handler = Mangum(app, lifespan="off")