import asyncio
import json
import logging

import tornado.httpclient

from requests.util import jsonize, ajsonize


async def request_details(oauth_session):
    client = tornado.httpclient.AsyncHTTPClient()
    header = {"Cookie": f"oauth-session={oauth_session}"}
    ret = None
    try:
        ret = await client.fetch("https://fiu.tips/oauth/details", headers=header)
    except tornado.httpclient.HTTPError as e:
        logging.info(f"HttpException: {str(e)}")
    except Exception as e:
        logging.info(f"Other exception: {str(e)}")
    client.close()
    return ret


@ajsonize
async def request_details_json(oauth_session):
    return await request_details(oauth_session)


def sync_request_details(oauth_session):
    client = tornado.httpclient.HTTPClient()
    ret = None
    try:
        header = {"Cookie": f'oauth-session={oauth_session}'}
        ret = client.fetch("https://fiu.tips/oauth/details", headers=header)
    except tornado.httpclient.HTTPError as e:
        logging.info(str(e))
    except Exception as e:
        logging.info(str(e))
    client.close()
    return ret


@jsonize
def sync_request_details_json(oauth_session):
    return sync_request_details(oauth_session)


if __name__ == "__main__":
    cookie = "MTU4NzkzNjg5MXxEdi1CQkFFQ180SUFBUkFCRUFBQWR2LUNBQUVHYzNSeWFXNW5EQTBBQzI5aGRYUm9MWFJ2YTJWdURTcHZZWFYwYURJdVZHOXJaVzdfZ3dNQkFRVlViMnRsYmdIX2hBQUJCQUVMUVdOalpYTnpWRzlyWlc0QkRBQUJDVlJ2YTJWdVZIbHdaUUVNQUFFTVVtVm1jbVZ6YUZSdmEyVnVBUXdBQVFaRmVIQnBjbmtCXzRZQUFBQVFfNFVGQVFFRVZHbHRaUUhfaGdBQUFISF9oRzRCSGpNd2VtODVOemw2YjNrNVltZ3pjWGMwWVhscGFYRTJlbVZtYW5jNFlRRUdZbVZoY21WeUFUSmplbkZ6T0dGaWVXOW5iVEJ5TmpJeGFqWjNjbWhxWkhCNmF6VnJiWGswZEhNMWVtaHBkMkpzYkdFM2FIQjFZbTh5WndFUEFRQUFBQTdXT0MwaUhaTzVyUUFBQUE9PXzXN0HrOY8H9p5f_5VsUx0AA5GtNAycKK0b5lpb8Ia8dA=="
    # body = sync_request_details_json(cookie)
    loop = asyncio.get_event_loop()
    task = request_details_json(cookie)
    json = loop.run_until_complete(task)
    print(json)
    # print(body)
