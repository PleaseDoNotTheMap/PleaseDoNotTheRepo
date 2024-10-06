import ast
import json
import logging

import aiohttp
from aiohttp import web

# from download import Downloader
from landstat import API

routes = web.RouteTableDef()

logger = logging.getLogger('landstat')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] - %(message)s')

sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)


@routes.get('/')
async def index(request):
    return web.Response(text='Hello, World!')


@routes.post('/get-data')
async def get_data(request):
    data = await request.json()

    results = await request.app['api'].search({
        'collections': ast.literal_eval(data["collections"]),
        'bbox': ast.literal_eval(data['bbox']),
        'datetime': data["datetime"],
        'query': data["query"]
    })

    return web.Response(text=json.dumps(results), content_type='application/json')


@routes.get('/search')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for received in ws:
        if received.type == aiohttp.WSMsgType.TEXT:
            if received.data == 'close':
                await ws.close()
            else:
                message = json.loads(received.data)
                match message['type']:
                    case 'search':
                        results = await request.app['api'].search(message['query'])
                        await ws.send_str(json.dumps(results))
        elif received.type == aiohttp.WSMsgType.ERROR:
            print(f'Ws conn closed with exception {ws.exception()}')

    print('Websocket connection closed')

    return ws


async def main(app):
    session = aiohttp.ClientSession()
    # app['downloader'] = Downloader(session)
    app['api'] = await API(session).start()

    yield
    await session.close()


async def app_factory():
    app = web.Application()
    app.cleanup_ctx.append(main)
    app.add_routes(routes)
    return app


