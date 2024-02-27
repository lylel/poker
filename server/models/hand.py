import asyncio

from transitions import Machine

from logic.connection_manager import TableConnectionManager
from main import table_connection_manager
from models.round import Round
from models.deck import Deck
from commands.client import HoleCards, PostSmallBlind, PostBigBlind, UpdatePot, DealFaceDownHoleCards, PromptAction
from models.table import Table, Seat, Action


class Hand:
    states = [
        "init",
        "Preflop",
        "preflop_betting",
        "Flop",
        "Turn",
        "Flop_Betting",
        "Turn_Betting",
        "River",
        "River_Betting",
        "Showdown",
        "end",
    ]

    transitions = [
        {"trigger": "proceed", "source": "end", "dest": "init"},
        {"trigger": "proceed", "source": "init", "dest": "Preflop"},
        {"trigger": "proceed", "source": "Preflop", "dest": "preflop_betting"},
        {
            "trigger": "proceed",
            "source": "Preflop",
            "dest": "end",
            "condition": "is_only_one_left",
        },
        {"trigger": "proceed", "source": "preflop_betting", "dest": "Flop"},
        {"trigger": "proceed", "source": "Flop", "dest": "Flop_Betting"},
        {"trigger": "proceed", "source": "Flop_Betting", "dest": "Turn"},
        {"trigger": "proceed", "source": "Turn", "dest": "Turn_Betting"},
        {"trigger": "proceed", "source": "Turn_Betting", "dest": "River"},
        {"trigger": "proceed", "source": "River", "dest": "River_Betting"},
        {"trigger": "proceed", "source": "River_Betting", "dest": "Showdown"},
        {"trigger": "proceed", "source": "Showdown", "dest": "end"},
    ]

    def __init__(self, table, seats, sb, bb, sb_i, bb_i, button_i, is_heads_up):
        self.table: Table = table
        self.is_done = False
        self.bb = bb
        self.sb = sb
        self.seats: list[Seat] = seats
        self.sb_i = sb_i
        self.bb_i = bb_i
        self.is_heads_up = is_heads_up
        self.current_player_i = None
        self.live_round = None
        self.last_to_act = button_i
        self.pot = 0
        self.bets = []
        self.board = []
        self.current_betting_round = 0
        self.deck = Deck()
        self.machine = Machine(
            model=self, states=Hand.states, transitions=Hand.transitions, initial="init"
        )

        self.demand_blinds()

        self.live_round = Round(
            seats=self.seats,
            sb_i=sb_i,
            bb_i=bb_i,
            button_i=button_i,
            current_i=bb_i,
            bb=self.bb,
        )
        self.demand_blinds()
        self.deal_hole_cards()
        await asyncio.sleep(1)
        if self.is_heads_up:
            self.current_player_i = self.sb_i
        self.prompt_current_player(options=[Action.CALL, Action.RAISE, Action.FOLD])

    def get_seat_conn(self, seat_i):
        conn = table_connection_manager.get_connection(
            table_id=self.table._id, player_id=self.seats[seat_i].player_id
        )
        return conn

    def broadcast(self, update):
        for seat_i, seat in enumerate(self.seats):
            if seat:
                self.get_seat_conn(seat_i=seat_i).send_json(update)

    def demand_blinds(self):
        # TODO: Handle case where there's not enough blinds
        self.seats[self.sb_i].chips -= self.sb
        self.seats[self.sb_i].chips -= self.bb
        self.pot += self.sb + self.bb

        self.broadcast(PostSmallBlind(seat_i=self.sb_i, amount=self.sb).model_dump())
        self.broadcast(PostBigBlind(seat_i=self.bb_i, amount=self.bb).model_dump())
        self.broadcast(UpdatePot(total=self.pot).model_dump())

    def deal_hole_cards(self):
        for seat_i, seat in enumerate(self.seats):
            if seat and seat.is_sitting_in:
                self.get_seat_conn(seat_i=seat_i).send_json(HoleCards(cards=self.deck.draw_cards(2)).model_dump())
                # DO WE NEED
                # for other_seat_i, other_seat in enumerate(self.seats):
                #     if other_seat and other_seat_i != seat_i:
                #         self.get_seat_conn(seat_i=other_seat_i).send_json(
                #             DealFaceDownHoleCards(seat_i=seat_i).model_dump())

    def prompt_current_player(self, options):
        self.get_seat_conn(self.current_player_i).send_json(PromptAction(options=options))

    def on_exit_init(self):
        # Send response to current player
        # Prompt Action
        pass

    def on_enter_init(self):

        pass

    def on_enter_(self):
        pass

    @property
    def round_is_live(self):
        return True

    def start_betting_round(self):
        if self.state in ["Flop", "Turn", "River"]:
            self.start_betting()
            print(f"Started Betting Round {self.current_betting_round + 1}")
            self.current_betting_round += 1
        else:
            print("Cannot start betting round at the current state.")

    def end_betting_round(self):
        if self.state == "Betting":
            self.end_betting()
            print(f"ended Betting Round {self.current_betting_round}")
        else:
            print("Cannot end betting round at the current state.")



        def player_bet(self, player):
            if self.state == "Betting":
                print(f"{player} bets.")

        def player_fold(self, player):
            if self.state == "Betting":
                print(f"{player} folds.")

        def player_call(self, player):
            if self.state == "Betting":
                print(f"{player} calls.")

        def player_raise(self, player):
            if self.state == "Betting":
                print(f"{player} raises.")
