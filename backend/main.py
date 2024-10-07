import ast
import aiohttp_cors
import json
import logging
import os
import aiohttp
from aiohttp import web
from apscheduler.schedulers.background import BackgroundScheduler
import getMeta

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
    
    @routes.post('/delete')
    async def submit(request: aiohttp.web.Request):
        data = dict(await request.json())
        ret = request.app['this'].db.remove_notification(data["location"], data["email"])
        return web.Response(text=str(ret), content_type='text/html')

    @routes.post('/get-notifications')
    async def submit(request: aiohttp.web.Request):
        data = dict(await request.json())
        ret = request.app['this'].db.get_user_notifications(data["email"])
        return web.Response(text=str(ret), content_type='text/html')

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
        
    @routes.get('/download')
    async def submit(request: aiohttp.web.Request):
        try:
            data = await request.json()
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            getMeta.MetaData(longitude, latitude)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return web.Response(status=500, text="Internal Server Error")
        
    @routes.get('/data')
    async def send_json(request):
        # Load your JSON file
        with open('path/to/your/data.json', 'r') as f:
            data = json.load(f)
        # Send JSON response to the client
        return web.json_response(data)
            
    


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
