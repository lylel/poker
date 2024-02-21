import uuid
from enum import Enum

from models.hand import Hand


class CasinoFloor:
    def __init__(self):
        self.tables = {}

    def add_table(self, table_id, table):
        self.tables[table_id] = table

    def remove_table(self, table_id):
        pass


class Table:
    def __init__(self, name, max_seats, sb, bb):
        self._id = uuid.uuid4()
        self.name = name
        self.max_seats = max_seats
        self.sb = sb
        self.bb = bb
        self.seats = [None for _ in range(max_seats)]
        self.player_id_seat_map = {}
        self.round = None
        self.current_hand: Hand = None

    def continue_(self):
        if self.round.has_not_started:
            self.round.deal_hole_cards()
        else:
            pass

    def sit_player(self, player, seat):
        if not self.seats[seat - 1]:
            self.seats[seat - 1] = player.account_id
            self.player_id_seat_map[player.account_id] = self.seats[seat - 1]
            return True
        return False

    def new_hand(self, sb_i, bb_i, button_i):
        if self.current_hand.is_done:
            hand = Hand(seats=self.seats, sb=self.sb, bb=self.bb, sb_i=sb_i, bb_i=bb_i, button_i=button_i)
            self.current_hand = hand
            return True
        return False


class Deck:
    pass


class Board:
    def __init__(self):
        self.cards = []


class Action(Enum):
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    FOLD = "fold"


class SeatStatus(Enum):
    pass


class PlayerStatus(Enum):
    INIT = "init"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    FOLD = "fold"


class RoundState:
    START = "start"
    CHECKED = "checked"
    CALLED = "called"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all-in"
    END = "end"


class Seat:
    def __init__(self):
        self.state = PlayerStatus.INIT
        self.bet = 0
        self.raises = []

    def __repr__(self):
        return f"State: {self.state}, Bet: {self.bet}"


