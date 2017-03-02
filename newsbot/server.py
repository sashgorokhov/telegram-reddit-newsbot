import asyncio
from aiohttp import web
from newsbot import routes


def run_server(loop=None):
    """
    :param asyncio.AbstractEventLoop loop:
    """
    loop = loop or asyncio.get_event_loop()
    app = web.Application(loop=loop)
    routes.setup_routes(app)
    return web.run_app(app, host='0.0.0.0', port=80)
