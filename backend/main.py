import ast
import json
import logging

import aiohttp
from aiohttp import web
from apscheduler.schedulers.background import BackgroundScheduler

from landstat import API
from mailer import Mailer

routes = web.RouteTableDef()

logger = logging.getLogger('landstat')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] - %(message)s')

sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)


class App:
    def __init__(self):
        self.app = web.Application()
        self.app.cleanup_ctx.append(self._context)
        self.app.add_routes(routes)
        self.scheduler = BackgroundScheduler()

    @routes.post('/submit')
    async def submit(request):
        data = await request.json()

        return web.Response(text=json.dumps(data),
                            content_type='application/json')

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

    async def _context(self, app):
        self.session = aiohttp.ClientSession()
        app['api'] = await API(self.session).start()
        app['mailer'] = Mailer(self.session)

        yield
        await self.session.close()

    def run(self):
        web.run_app(self.app)


app = App()
app.run()
