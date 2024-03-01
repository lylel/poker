import asyncio
from collections import defaultdict

from starlette.websockets import WebSocket

from client_events.events import InvalidActionSubmittedEvent
from models.round import Round
from utils import timer


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


class TableEventManager:
    def __init__(self, table_id, seats, table_connection_manager):
        self.table_id = table_id
        self.seats = seats
        self.table_connection_manager = table_connection_manager

    def get_seat_conn(self, seat_i) -> WebSocket:
        conn = self.table_connection_manager.get_connection(
            table_id=self.table_id, player_id=self.seats[seat_i].player_id
        )
        return conn

    async def push_to_player(self, seat_i, event):
        await self.get_seat_conn(seat_i).send_json(event)

    def broadcast_to_seats(self, seats, event):
        pass

    async def broadcast_to_table(self, event):
        for seat_i, seat in enumerate(self.seats):
            if seat:
                await self.get_seat_conn(seat_i=seat_i).send_json(event)

    async def push_to_conn(self, conn: WebSocket, event):
        await conn.send_json(event)

    async def get_action_from_player(self, round, time_limit=60):
        get_action_task = asyncio.create_task(
            self.wait_for_event_from_player(round=round)
        )
        clock_task = asyncio.create_task(timer(time_limit))

        done, pending = await asyncio.wait(
            [get_action_task, clock_task], return_when=asyncio.FIRST_COMPLETED
        )

        return get_action_task.result() if get_action_task in done else None

    async def wait_for_event_from_player(self, round: Round):
        conn = self.get_seat_conn(round.current_seat_i)
        while True:
            action_event = await conn.receive_json()
            if round.act(action_event):
                return action_event
            else:
                await self.push_to_player(
                    seat_i=round.current_seat_i, event=InvalidActionSubmittedEvent()
                )


async def get_user_input(websocket: WebSocket):
    allowed_commands = ["call", "raise"]
    while True:
        action = await websocket.receive_text()
        if action in allowed_commands:
            print("did this work@@@@%^(*#&%OI*Y%OIYTOI@YTUIOYUT")
            return action
        else:
            await websocket.send_text("Invalid command. Please enter a valid command.")
