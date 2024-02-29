from fastapi import FastAPI

from global_state import table_manager
from logic.connection_manager import TableConnectionManager

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from logic.table_manager import create_table

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


table_connection_manager = TableConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.post("/admin/table")
def create_admin_table(request_data):
    table_manager.create_table(request_data)
    print(table_manager.get_tables())


#
#
# @app.websocket("/admin/table/")
# async def administrate_table(websocket: WebSocket):
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
#
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
