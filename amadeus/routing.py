from channels.routing import route
from mural.consumers import ws_message

channel_routing = [
    route("websocket.receive", ws_message),
]