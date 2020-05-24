import json
import logging
import uuid
import aiofiles
from queue import SimpleQueue
from typing import Any
import csv

import tornado.ioloop
import tornado.web
from tornado import httputil

import tornado.websocket

from handlers.util import msg_to_json, send_error_message, required_in_json, required_state, set_state, \
    send_error_message_and_close, required_in_cookies
from requests.oauth import request_details_json

MAX_SIZE = 1024 * 1024


class SoundListenerHandler(tornado.websocket.WebSocketHandler):
    listeners = set()
    allowed_listeners = list(map(str.casefold,
                                 ['FriendlyFiutonaczi', ])
                             )

    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self.handlers = {
            'hello': self.hello_handler,
        }
        self.oauth_details = None
        self.auth_cookie = None

    def check_origin(self, origin):
        return True

    @required_in_json("oauth-session")
    @required_state(None)
    async def hello_handler(self, msg):
        oauth_session = msg['oauth-session']
        details = await request_details_json(oauth_session)

        if details is None:
            return await send_error_message_and_close(self, "Failed to get details from oauth-session cookie")
        if details["display_name"].casefold() not in SoundListenerHandler.allowed_listeners:
            return await send_error_message_and_close(self,
                                                      f"You {details['display_name']}"
                                                      f" are not allowed to listen to clips. "
                                                      f"Only {SoundListenerHandler.allowed_listeners} can listen!")

        self.oauth_details = details
        self.auth_cookie = oauth_session
        SoundListenerHandler.listeners.add(self)
        set_state(self, "authorized")
        return self.write_message(json.dumps({"status": "ok"}))

    @msg_to_json
    @required_in_json("intent")
    async def on_message(self, message):
        return self.handlers[message["intent"]](message)

    def open(self):
        pass

    def on_connection_close(self):
        self.on_finish()

    def on_finish(self):
        if self in SoundListenerHandler.listeners:
            SoundListenerHandler.listeners.remove(self)


class SoundPushHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self.auth_cookie = None
        self.oauth_details = None
        self.handlers = {
            'hello': self.hello_handler,
            'push': self.push_handler
        }

    def check_origin(self, origin):
        return True

    def open(self):
        pass

    @msg_to_json
    @required_in_json("intent")
    async def on_message(self, message):
        return self.handlers[message["intent"]](message)

    @required_in_json("oauth-session")
    @required_state(None)
    async def hello_handler(self, msg):
        oauth_session = msg['oauth-session']
        details = await request_details_json(oauth_session)

        if details is None:
            raise ValueError("Didn't get details from oauth-session")

        self.oauth_details = details
        self.auth_cookie = oauth_session
        set_state(self, "authorized")
        return self.write_message(json.dumps({"status": "ok"}))

    @required_in_json("path")
    @required_state("authorized")
    async def push_handler(self, msg):
        for listener in SoundListenerHandler.listeners:
            try:
                listener.write_message(json.dumps(
                    {"path": msg["path"], "from_display_name": self.oauth_details["display_name"],
                     "from_id": self.oauth_details["id"]}))
            except tornado.websocket.WebSocketClosedError as e:
                logging.info(e)
        return self.write_message(json.dumps({"status": "ok", "listeners": len(SoundListenerHandler.listeners)}))

    async def on_close(self):
        pass


class SoundUploadHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ["POST"]

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        self.details = None
        super().__init__(application, request, **kwargs)

    def check_origin(self, origin):
        return True

    @required_in_cookies("oauth-session")
    async def post(self):
        self.details = await request_details_json(self.request.cookies["oauth-session"].value)
        if self.details is None:
            return self.write_error(401)
        for field_name, files in self.request.files.items():
            meta = []
            for info in files:
                meta.append(await self.save_sound(info))
            await self.save_meta(meta)
        return self.write(json.dumps({"status": "ok"}))

    async def save_sound(self, info):
        filename, content_type = info["filename"], info["content_type"]
        body = info["body"]
        logging.info(
            'POST "%s" "%s" %d bytes.', filename, content_type, len(body)
        )
        _uuid = uuid.uuid4()
        async with aiofiles.open(f'uploads/{_uuid}_{filename}', "wb") as file:
            await file.write(body)
            return f"{self.details['id']};{self.details['display_name']};{_uuid};{filename.strip()}\n"

    async def save_meta(self, meta):
        async with aiofiles.open(f'uploads/meta', "a") as meta_csv:
            await meta_csv.writelines(meta)
        for row in meta:
            MetaRequestHandler.load_row(row.split(';'))


class MetaRequestHandler(tornado.web.RequestHandler):
    meta = []

    @staticmethod
    def load_meta():
        with open("uploads/meta", "a+") as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                MetaRequestHandler.load_row(row)

    @staticmethod
    def load_row(row):
        user_id, display_name, _uuid, filename = row
        MetaRequestHandler.meta.append({"uuid": _uuid,
                                        "user_id": user_id,
                                        "display_name": display_name.strip(),
                                        "filename": filename.strip(),
                                        "path": f"/api/uploads/{_uuid}_{filename.strip()}"
                                        })

    def get(self):
        self.write(json.dumps(MetaRequestHandler.meta))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    return tornado.web.Application([
        (r"/api/uploads/(.*)", tornado.web.StaticFileHandler, {"path": "/app/uploads/"}),
        (r"/ws/push", SoundPushHandler),
        (r"/ws/listen", SoundListenerHandler),
        (r"/api/upload", SoundUploadHandler),
        (r"/api/meta", MetaRequestHandler)
    ])


if __name__ == "__main__":
    MetaRequestHandler.load_meta()
    logging.root.setLevel('INFO')
    app = make_app()
    server = tornado.web.HTTPServer(app, max_body_size=MAX_SIZE)
    server.listen(8888)
    tornado.ioloop.IOLoop.current().start()
