import copy
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


class Seat:
    def __init__(self, player_id, chips, sitting_in=False):
        self.player_id = player_id
        self.chips = chips
        self.is_sitting_in = sitting_in


class Table:
    def __init__(self, name, max_seats, sb, bb):
        self.tid = uuid.uuid4()
        self.name = name
        self.max_seats = max_seats
        self.sb = sb
        self.bb = bb
        self.seats: list[Seat | None] = [None for _ in range(max_seats)]
        self.player_id__seat_i_map = {}
        self.round = None
        self.current_hand: Hand | None = None
        self.current_sb = None
        self.current_bb = None

    def continue_(self):
        if self.round.has_not_started:
            self.round.deal_hole_cards()
        else:
            pass

    def new_hand(self, sb_i, bb_i, button_i):
        if self.current_hand.is_done:
            self.current_hand = Hand(
                table=self,
                seats=copy.deepcopy(self.seats),
                sb=self.sb,
                bb=self.bb,
                sb_i=sb_i,
                bb_i=bb_i,
                button_i=button_i,
                is_heads_up=self.is_heads_up,
            )
            return True
        return False

    def post_small_blind(self, account_id):
        pass

    def post_big_blind(self, account_id):
        pass

    def assign_blinds(self):
        if not self.has_minimum_players_to_start:
            return False

        if self.current_sb and self.current_bb:
            self.current_sb = self.current_bb

            while any(
                not self.seats[self.current_bb]
                or not self.seats[self.current_bb].is_sitting_in
                for _ in range(self.max_seats)
            ):
                self.current_bb = (self.current_bb + 1) % self.max_seats

    def sit_player_down(self, player_id, seat_i, chips):
        if not 0 <= seat_i < self.max_seats or self.seats[seat_i]:
            return False

        self.seats[seat_i] = Seat(player_id=player_id, chips=chips, sitting_in=False)
        self.player_id__seat_i_map[player_id] = seat_i
        return True

    def sit_player_in(self, player_id, seat_i):
        if not 0 <= seat_i < self.max_seats:
            return False
        # Check for auth
        self.seats[seat_i].is_sitting_in = True

        if not self.current_hand and self.has_minimum_players_to_start:
            self._set_starting_blinds(seat_i)
            self._start_new_game()
        return True

    def sit_player_out(self, player_id, seat_i):
        if not 0 <= seat_i < self.max_seats:
            return False
            # Check for auth
        self.seats[seat_i].is_sitting_in = False

    def _start_new_game(self):
        self.current_hand = Hand(
            seats=self.seats,
            sb=self.sb,
            bb=self.bb,
            sb_i=self.current_sb,
            bb_i=self.current_bb,
            button_i=self.current_sb,
        )
        self.current_hand.proceed()

    def _set_starting_blinds(self, seat_i):
        self.current_bb = seat_i
        for i in range(len(self.seats)):
            if i != self.current_bb and self.seats[i] and self.seats[i].is_sitting_in:
                self.current_sb = i

    def unseat_player(self, player_id):
        for i, seat in enumerate(self.seats):
            if seat and seat.player_id == player_id:
                self.seats[i] = None
                self.player_id__seat_i_map[player_id] = None
                return True
        return False

    @property
    def active_players_count(self):
        return sum(
            1
            for seat in self.seats
            if seat and seat.is_sitting_in and seat.chips >= self.bb
        )

    @property
    def has_minimum_players_to_start(self):
        return self.active_players_count > 1

    @property
    def is_heads_up(self):
        return sum(1 for player in self.seats if player and player.is_sitting_in) == 2

    def __str__(self):
        return f"Table Name: {self.name}, Max Players: {self.max_seats}, Small Blind: {self.sb}, Big Blind: {self.bb}"


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
