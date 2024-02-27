from collections import defaultdict

from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class TableConnectionManager(ConnectionManager):
    def __init__(self):
        super().__init__()
        self._table_player_connection_map = defaultdict(dict)

    async def connect_to_table(self, table_id, player_id, websocket: WebSocket):
        self._table_player_connection_map[table_id][player_id] = websocket
        await websocket.accept()

    async def disconnect_from_table(self, table_id, player_id, websocket: WebSocket):
        self._table_player_connection_map[table_id][player_id] = websocket
        await websocket.accept()

    def get_connection(self, player_id, table_id) -> WebSocket:
        return self._table_player_connection_map.get(table_id, {}).get(player_id, None)
