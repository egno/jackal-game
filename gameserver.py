from game.main import Game
from common.coordinates import Coord
from common.utils import GameEncoder
import datetime
import json

import asyncio
from aiohttp import web, WSMsgType
from faker import Faker

import logging


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


def get_game(app, id):
    game = app['games'].get(id)
    if game is None:
        game = GameServer()
        app['games'][id] = game
        app['websockets'][id] = {}
    return game


async def http_get_handler(request):
    id = request.match_info['id']
    game = get_game(request.app, id)
    return web.json_response(game.to_json(), dumps=dumps)


async def http_post_handler(request):
    data = await request.json()
    id = request.match_info['id']
    game = get_game(request.app, id)
    result = processData(game, data)
    return web.json_response(result, dumps=dumps)


async def send_to_game(app, id, message):
    for name in app['websockets'][id]:
        try:
            await app['websockets'][id][name].send_json(message, dumps=dumps)
        except Exception as e:
            log.error('Error %s', e)
            del app['websockets'][id][name]


async def websocket_handler(request):
    id = request.match_info['id']
    game = get_game(request.app, id)
    ws = web.WebSocketResponse(heartbeat=60, autoping=True, receive_timeout=90)
    await ws.prepare(request)

    name = Faker().name()
    log.info('%s joined.', name)

    await send_to_game(request.app, id, {'action': 'connect', 'name': name})

    request.app['websockets'][id][name] = ws

    async for msg in ws:

        if msg.type == WSMsgType.text:
            if msg.data == 'restart':
                game = GameServer()
                request.app['games'][id] = game
                await send_to_game(request.app, id, game.to_json())
                continue
            if msg.data == 'open':
                game.game.openAll()
                await send_to_game(request.app, id, game.to_json())
                continue
            if msg.data == 'close':
                await send_to_game(request.app, id, {"action": "close"})
                break
            if msg.data == 'status':
                await ws.send_json({'id': id, 'websockets': [
                    s for s in request.app['websockets'][id]
                ]})
                continue
            result = None
            try:
                result = processData(game, json.loads(msg.data))
            except Exception as e:
                log.error('Error: %s, Wrong socket data: %s', e, msg.data)
            if result is not None:
                await send_to_game(request.app, id, result)
        else:
            continue

    del request.app['websockets'][id][name]
    log.info('%s disconnected.', name)
    send_to_game({'action': 'disconnect', 'name': name})

    return ws


async def shutdown(app):
    for id in app['websockets']:
        for ws in app['websockets'][id].values():
            await ws.close()
            app['websockets'][id].clear()
    app['websockets'].clear()


def create_runner():
    app = web.Application()
    app.add_routes([
        web.get('/{id}',  http_get_handler),
        web.post('/{id}', http_post_handler),
        web.get('/ws/{id}', websocket_handler),
    ])
    app['games'] = {}
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
