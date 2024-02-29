from models.table import Table


class TableManager:
    def __init__(self):
        self._table_id_map: dict[str, Table] = {}

    def get_table_by_id(self, tid: str):
        return self._table_id_map.get(tid)

    def create_table(self, request_data):
        name = request_data["name"]
        max_seats = request_data["maxSeats"]
        sb = request_data["sb"]
        bb = request_data["bb"]

        table = Table(name=name, max_seats=max_seats, sb=sb, bb=bb)
        self.add_table(table)
        print(table)
        return table

    def add_table(self, table):
        self._table_id_map[table.tid] = table

    def get_tables(self):
        return self._table_id_map
