#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import fastapi
import requests
import pytube
import moviepy
import bs4
import youtubesearchpython


api = fastapi.FastAPI()


@api.get('/')
def root():
    return {
        "message": "Hello World"
    }
