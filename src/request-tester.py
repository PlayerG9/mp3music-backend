#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from pprint import pprint
import requests


url = r""
payload = dict(

) or None

response = requests.get(url, json=payload)

print(response.status_code)
pprint(response.json())
