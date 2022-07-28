#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
import importlib

import fastapi
from fastapi.responses import RedirectResponse

import scripts


__author__ = "PlayerG9"
__copyright__ = "Copyright 2021, PlayerG9"
__credits__ = ["PlayerG9"]
__version_info__ = (0, 1, 0)
__version__ = '.'.join(str(_) for _ in __version_info__)
__maintainer__ = "PlayerG9"
__email__ = None
__status__ = "Prototype"


app = fastapi.FastAPI(
    title="mp3music",
    description=scripts.getApiDescription(),
    version=__version__
)


@app.get('/', include_in_schema=False)
def index():
    return RedirectResponse(app.redoc_url)


@app.get('/mp3music/{path:path}', include_in_schema=False)
def interface(path: str):
    return RedirectResponse(f"https://playerg9.github.io/mp3music/{path}")


api = fastapi.APIRouter(prefix="/api")


for endpoint in os.listdir('endpoints'):
    importlib.import_module(f'endpoints.{endpoint}')


app.include_router(api)
