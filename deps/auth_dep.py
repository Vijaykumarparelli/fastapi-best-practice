from typing import Annotated

from fastapi import Depends

from config.db import DBSession
from controllers.auth_controller import AuthController


def init_auth_controller(session: DBSession):
    return AuthController(session)


AuthControllerDep = Annotated[AuthController, Depends(init_auth_controller)]
