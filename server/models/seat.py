from models.enums import PlayerStatus


class Seat:
    def __init__(self, player_id, chips, sitting_in=True):
        self.player_id = player_id
        self.chips = chips
        self.is_sitting_in = sitting_in
        self.cards = []
        self.has_folded = True
        self.chips_put_in = 0

    def set_hole_cards(self, cards):
        self.cards = cards

    def new_hand(self):
        self.has_folded = False
        self.cards = []

    def next_round(self):
        self.chips_put_in = 0
