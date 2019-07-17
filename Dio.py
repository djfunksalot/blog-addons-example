#!/usr/bin/env python
# WS client example
import asyncio
import websockets
import json
#hardware interface
class Dio(object):
    def __init__(self,master):
        self.master = master
        self.state = False
        print(self)
    async def syncit():
        async with websockets.connect(
                'ws://padio:6789') as websocket:
            name = json.dumps({'action': 'minus_vG'})

            await websocket.send(name)
            print(f"> {name}")

            greeting = await websocket.recv()
            print(f"< {greeting}")
    #initialize power supplies and parallel port
    asyncio.get_event_loop().run_until_complete(syncit())
