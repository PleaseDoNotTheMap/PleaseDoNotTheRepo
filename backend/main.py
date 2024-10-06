import ast
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

    @routes.get('/')
    async def index(request):
        return web.Response(text='Server is up!', content_type='text/html')

    @routes.post('/submit')
    async def submit(request: aiohttp.web.Request):
        data = await request.json()

        # NEED PUT THIS IN SIGNUP.html:   const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        # (name, email, notify_date, flyover_date, location)
        results = await Database.add_notification((
            data['username']
            ,data['email']
            # ,data[]
            # .data[]
            # Still need to configure notify date, and flyover date
            ,data['location'] 
        ), data.get('timezone', 'UTC'))

        return web.Response(text=json.dumps(data),
                            content_type='application/json')

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

    def run(self):
        self.scheduler.add_job(self.db.send_notifications, 'interval', minutes=60)
        self.scheduler.start()

        web.run_app(self.app)


app = App()
app.run()
