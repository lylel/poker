import asyncio

from transitions import Machine

from logic.connection_manager import TableEventManager
from main import table_connection_manager
from models.round import Round
from models.deck import Deck
from client_events.events import (
    HoleCards,
    SeatPostedSmallBlind,
    SeatPostedBigBlind,
    UpdatePot,
    PromptAction, CheckedEvent, ACTION_EVENT_MAP,
)
from models.table import Table, Seat, Action
from utils import timer


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
        self.deck = Deck()
        self.event_manager = TableEventManager(
            table_id=self.table.tid,
            seats=self.seats,
            table_connection_manager=table_connection_manager,
        )
        self.machine = Machine(
            model=self, states=Hand.states, transitions=Hand.transitions, initial="init"
        )
        self.demand_blinds()

        if self.is_heads_up:
            self.current_player_i = self.sb_i

        self.live_round = Round(
            seats=self.seats,
            sb_i=sb_i,
            bb_i=bb_i,
            button_i=button_i,
            current_i=bb_i,
            bb=self.bb,
        )

        await asyncio.sleep(1)

        self.proceed()

    def on_enter_preflop(self):
        self.deal_hole_cards()
        while not self.live_round.is_done:
            # TODO: Figure out options
            self.prompt_current_player(options=[Action.CALL, Action.RAISE, Action.FOLD])
        self.proceed()

    def on_enter_turn(self):
        # Does this need to be a new object everytime
        self.live_round = Round()
        # TODO: don't allow players to sit in in the middle of a hand
        while not self.live_round.is_done:
            # TODO: Figure out options
            self.prompt_current_player(options=[Action.CALL, Action.RAISE, Action.FOLD])
        self.proceed()

    def on_enter_river(self):
        pass

    def on_enter_showdown(self):
        pass

    def demand_blinds(self):
        # TODO: Handle case where there's not enough blinds
        self.seats[self.sb_i].chips -= self.sb
        self.seats[self.sb_i].chips -= self.bb
        self.pot += self.sb + self.bb

        self.event_manager.broadcast_to_table(
            SeatPostedSmallBlind(seat_i=self.sb_i, amount=self.sb).model_dump()
        )
        self.event_manager.broadcast_to_table(
            SeatPostedBigBlind(seat_i=self.bb_i, amount=self.bb).model_dump()
        )
        self.event_manager.broadcast_to_table(UpdatePot(total=self.pot).model_dump())

    def deal_hole_cards(self):
        for seat_i, seat in enumerate(self.seats):
            if seat and seat.is_sitting_in:
                self.event_manager.push_to_player(
                    seat_i=seat_i,
                    event=HoleCards(cards=self.deck.draw_cards(2)).model_dump(),
                )
                # DO WE NEED
                # for other_seat_i, other_seat in enumerate(self.seats):
                #     if other_seat and other_seat_i != seat_i:
                #         self.get_seat_conn(seat_i=other_seat_i).send_json(
                #             DealFaceDownHoleCards(seat_i=seat_i).model_dump())


    def prompt_current_player(self, options, time):
        self.event_manager.push_to_player(
            self.current_player_i, PromptAction(options=options)
        )

        action = asyncio.create_task(self.event_manager.wait_for_event_from_seat(seat_i=self.current_player_i, round=self.live_round))
        clock_task = asyncio.create_task(timer(time))

        done, pending = await asyncio.wait([action, clock_task], return_when=asyncio.FIRST_COMPLETED)

        if action in done:
            action_event = action.result()

            self.event_manager.broadcast_to_table(
                event=ACTION_EVENT_MAP[action_event["type"](seat_i=self.current_player_i, table_id=self.table.tid)))

        else:
            #TODO: FIX
            if self.live_round.all_checked:
                self.event_manager.broadcast_to_table(event=CheckedEvent(seat_i=self.current_player_i, table_id=self.table.tid))

            # event_manager
