import json
import logging


async def send_error_message(self, msg):
    ans = json.dumps({"error": msg})
    sender = self.write_message if hasattr(self, 'write_message') else self.write
    logging.error(ans)
    return await sender(ans)


async def send_error_message_and_close(self, msg):
    try:
        await send_error_message(self, msg)
        return await self.close()
    except:
        pass


def msg_to_json(func):
    async def wrapper(self, msg):
        try:
            msg = json.loads(msg)
            return await func(self, msg)
        except json.JSONDecodeError as e:
            reply = json.dumps({"error": f"failed to decode json err: {str(e)}"})
            return await send_error_message(self, msg)

    return wrapper


def required_in_cookies(*args):
    def _required_in_cookies(func):
        async def wrapper(self):
            if all(arg in self.cookies for arg in args):
                return await func(self)
            else:
                return await send_error_message(self,
                                                f"You didn't provide these fields in cookies: "
                                                f"{str(list(filter(lambda arg: arg not in args, args)))}. Context args: {list(args)}")

        return wrapper

    return _required_in_cookies


def required_in_json(*args):
    def _required_in_json(func):
        async def wrapper(self, msg):
            if all(arg in msg for arg in args):
                return await func(self, msg)
            else:
                return await send_error_message(self,
                                                f"You didn't provide these fields in json: "
                                                f"{str(list(filter(lambda arg: arg not in args, args)))}. Context args: {list(args)}")

        return wrapper

    return _required_in_json


def required_state(*args):
    def _required_state(func):
        async def wrapper(self, msg):
            state = self._decor_state if hasattr(self, '_decor_state') else None
            if state not in args:
                return await send_error_message(self, f"Invalid state expected (any of): {args}, got {state}")
            return await func(self, msg)

        return wrapper

    return _required_state


def set_state(self, state):
    self._decor_state = state
