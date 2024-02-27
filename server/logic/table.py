from models.table import Table


def create_table(request_data):
    name = request_data["name"]
    max_seats = request_data["maxSeats"]
    sb = request_data["sb"]
    bb = request_data["bb"]

    table = Table(name=name, max_seats=max_seats, sb=sb, bb=bb)
    print(table)
    return table
