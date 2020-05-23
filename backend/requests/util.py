import functools
import json
import logging

import tornado.httpclient


def ajsonize(func):
    async def closure(*args, **kwargs):
        try:
            req = await func(*args, **kwargs)
            return json.loads(req.body)
        except tornado.httpclient.HTTPClientError as e:
            logging.info(f'HTTPClientError: {e}')
        except Exception as e:
            logging.info(f'Some exception: {e}')

    return closure


def jsonize(func):
    def closure(*args, **kwargs):
        try:
            return json.loads(func(*args, **kwargs).body)
        except tornado.httpclient.HTTPClientError as e:
            logging.info(e)
        except Exception as e:
            logging.info(e)

    return closure
