from models.enums import PlayerStatus


class Seat:
    def __init__(self, player_id, chips, sitting_in=True):
        self.player_id = player_id
        self.chips = chips
        self.is_sitting_in = sitting_in
        self.state = PlayerStatus.INIT
        self.chips_put_in = 0
