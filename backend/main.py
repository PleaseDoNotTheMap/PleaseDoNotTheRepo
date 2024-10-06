import ast
import aiohttp_cors
import json
import logging

import aiohttp
from aiohttp import web
from apscheduler.schedulers.background import BackgroundScheduler

from database import Database
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
        self.mailer = Mailer()
        self.db = Database('user_notifications.db')

        self._setup_cors()

    @routes.get('/')
    async def index(request):
        return web.Response(text='Server is up!', content_type='text/html')

    @routes.post('/submit')
    async def submit(request: aiohttp.web.Request):
        data = dict(await request.json())
        payload = tuple(list(data.values()))

        if(payload[3] == 0):
            return

        ret = request.app['this'].db.add_notification(payload)
        return web.Response(text=str(ret), content_type='text/html')

    @routes.post('/get-data')
    async def get_data(request: aiohttp.web.Request):
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
                logger.info("Ws conn closed with {ws.exception()}")

        logger.info(f"Ws conn closed")

        return ws

    async def _context(self, app):
        self.session = aiohttp.ClientSession()
        app['api'] = await API(self.session).start()
        app['this'] = self

        yield
        await self.session.close()

    def _setup_cors(self):
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
        })

        for route in list(self.app.router.routes()):
            cors.add(route)

    def run(self):
        self.scheduler.add_job(self.db.send_notifications, 'interval', minutes=60)
        self.scheduler.start()

        web.run_app(self.app)


app = App()
app.run()
