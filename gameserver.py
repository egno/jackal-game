from game.main import Game
from common.coordinates import Coord
from common.utils import GameEncoder
import datetime
import json

import asyncio
from aiohttp import web, WSCloseCode, WSMsgType
from faker import Faker

import logging


GS = {}
log = logging.getLogger(__name__)


class GameServer(object):
    def __init__(self):
        self.game = Game()
        self.ts = datetime.datetime.now()

    def move(self, item: int, x: int, y: int):
        return self.game.moveItem(item, Coord(x, y))

    def to_json(self):
        info = self.game.to_json()
        info['ts'] = f'{self.ts}'
        return info


def dumps(data):
    return json.dumps(data, cls=GameEncoder)


def processData(game, data):
    if isinstance(data, list):
        for m in data:
            item = int(m.get('item'))
            x = int(m.get('x'))
            y = int(m.get('y'))
            success = game.move(item, x, y)
    else:
        item = int(data.get('item'))
        x = int(data.get('x'))
        y = int(data.get('y'))
        success = game.move(item, x, y)
    result = game.to_json()
    result['success'] = success
    return result


async def http_get_handler(request):
    return web.json_response(request.app['game'].to_json(), dumps=dumps)


async def http_post_handler(request):
    data = await request.json()
    result = processData(request.app['game'], data)
    return web.json_response(result, dumps=dumps)


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    name = Faker().name()
    log.info('%s joined.', name)

    await ws.send_json({'action': 'connect', 'name': name})

    for w in request.app['websockets'].values():
        try:
            await w.send_json({'action': 'join', 'name': name})
        except RuntimeError as e:
            log.error('Error %s', e)
            del request.app['websockets'][name]
    request.app['websockets'][name] = ws

    while True:
        msg = await ws.receive()

        if msg.type == WSMsgType.text:
            print(request.app['websockets'])
            result = None
            try:
                result = processData(request.app['game'], json.loads(msg.data))
            except Exception as e:
                log.error('Error: %s, Wrong socket data: %s', e, msg.data)
            if result is not None:
                for w in request.app['websockets'].values():
                    await w.send_json(result, dumps=dumps)
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for w in request.app['websockets'].values():
        await w.send_json({'action': 'disconnect', 'name': name})

    return ws


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
        app['websockets'].clear()


def create_runner():
    app = web.Application()
    app.add_routes([
        web.get('/',  http_get_handler),
        web.post('/', http_post_handler),
        web.get('/ws', websocket_handler),
    ])
    app['game'] = GS.get(id, GameServer())
    app['websockets'] = {}
    app.on_shutdown.append(shutdown)
    return web.AppRunner(app)


async def start_server(host="0.0.0.0", port=8000):
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
