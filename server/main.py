import asyncio

import uvicorn
from fastapi import FastAPI

from global_state import table_manager
from logic.connection_manager import TableConnectionManager, TableEventManager
from models.hand import Hand
from models.seat import Seat

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


from fastapi import FastAPI, WebSocket


app = FastAPI()


table_connection_manager = TableConnectionManager()

TABLE_ID_HAND_MAP: dict[str, Hand] = {}


@app.get("/start")
async def get():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)
    seats = [seat_1, seat_2]
    event_manager = TableEventManager(table_id="abc", seats=seats, table_connection_manager=table_connection_manager)

    await event_manager.broadcast_to_table({"hi": "bye"})
    hand = Hand(
        seats=[seat_1, seat_2],
        sb=5,
        bb=10,
        sb_i=0,
        bb_i=1,
        event_manager=event_manager,
    )
    await hand.begin_preflop()
    return {"hello": "ok"}


@app.post("/admin/table")
def create_admin_table(request_data):
    table_manager.create_table(request_data)
    print(table_manager.get_tables())


#
#
@app.websocket("/table/{table_id}/player/{player_id}")
async def connect(table_id, player_id, websocket: WebSocket):
    await table_connection_manager.connect_to_table(table_id, player_id, websocket)
    while True:
        await asyncio.sleep(30)



#
# @app.websocket("/table/{table_id}")
# async def administrate_table(
#     websocket: WebSocket,
#     table_id: str,
# ):
#     print("Got to 1")
#     await manager.connect(websocket)
#     print("Got to 2")
#     try:
#         while True:
#             print("Got to 3")
#
#             request_data = await websocket.receive_json()
#             print("Got to 4")
#
#             table = create_table(request_data)
#             await manager.send_personal_message(f"You wrote: {table}", websocket)
#             # await manager.broadcast(f"Client #{client_id} says: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"Client  left the chat")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)