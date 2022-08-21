#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from pydantic import BaseModel
from main import api


class HelloWorldModel(BaseModel):
    message: str = "Hello World"


@api.get(
    '/',
    name="hello-world",
    response_model=HelloWorldModel
)
def root():
    return {
        "message": "Hello World"
    }


# @api.get(
#     '/test',
# )
# def test(
#         val: str = Query()
# ):
#     return {
#         "obj": val
#     }
