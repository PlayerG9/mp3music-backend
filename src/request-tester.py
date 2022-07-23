#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from pprint import pprint
import json
import requests
import asyncio
import websockets
import websockets.legacy.client


ID = "ha-edv6PVqY"
url = f"ws://127.0.0.1:5000/api/download/{ID}"
payload = dict(
    metadata=dict(
        title="I'M ALRIGHT!",
        artist="Sportfreunde Stiller"
    )
) or None


async def main():
    async with websockets.connect(url) as websocket:
        websocket: websockets.legacy.client.WebSocketClientProtocol
        await websocket.send(json.dumps(payload))
        while not websocket.closed:
            message = await websocket.recv()
            data = json.loads(message)
            pprint(data)


asyncio.run(main())


# response = requests.get(url, json=payload)
# print(response.status_code)
# pprint(response.json())
