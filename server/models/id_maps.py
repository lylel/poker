import uuid

from models.table import Table

TABLE_ID_TABLE_MAP: dict[uuid, Table] = {}
PLAYER_ID_TABLES_MAP: dict[uuid, list[uuid]] = {}
PLAYER_ID__TABLE_ID__WEBSOCKET_MAP = {}
