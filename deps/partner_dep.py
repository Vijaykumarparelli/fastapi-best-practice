from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from config.db import DBSession
from controllers.partner_controller import PartnerController


def init_partner_controller(session: DBSession):
    return PartnerController(session)


PartnerControllerDep = Annotated[PartnerController, Depends(init_partner_controller)]

PartnerLoginFormData = Annotated[OAuth2PasswordRequestForm, Depends()]
