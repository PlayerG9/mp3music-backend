#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from main import api
from pydantic import BaseModel


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
