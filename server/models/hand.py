import asyncio

from transitions import Machine


from models.round import Round
from models.deck import Deck
from client_events.events import (
    HoleCards,
    SeatPostedSmallBlind,
    SeatPostedBigBlind,
    UpdatePot,
    PromptAction, ACTION_EVENT_MAP, CheckEvent,
)
from models.enums import Action
from models.seat import Seat
from utils import timer


class Hand:
    states = [
        "init",
        "preflop",
        "flop",
        "turn",
        "river",
        "showdown",
        "end",
    ]

    transitions = [
        {"trigger": "proceed", "source": "end", "dest": "init"},
        {"trigger": "proceed", "source": "init", "dest": "preflop"},
        {"trigger": "proceed", "source": "preflop", "dest": "flop"},
        {
            "trigger": "proceed",
            "source": "preflop",
            "dest": "end",
            "conditions": "is_only_one_left",
        },
        {"trigger": "proceed", "source": "flop", "dest": "turn"},
        {"trigger": "proceed", "source": "turn", "dest": "river"},
        {"trigger": "proceed", "source": "river", "dest": "showdown"},
        {"trigger": "proceed", "source": "showdown", "dest": "end"},
    ]

    def __init__(
        self, seats, sb, bb, sb_i, bb_i, event_manager, pause_between_rounds=1
    ):
        self.seats: list[Seat] = seats
        self.sb = sb
        self.bb = bb
        self.sb_i = sb_i
        self.bb_i = bb_i
        self.last_to_act = self.bb_i
        self.pause_between_rounds = pause_between_rounds
        self.pot = 0
        self.board = []
        self.deck = Deck()
        self.event_manager = event_manager
        self.round = Round(
            seats=self.seats,
            first_to_act_i=sb_i,
            min_raise=self.bb,
        )
        self.machine = Machine(
            model=self, states=Hand.states, transitions=Hand.transitions, initial="init"
        )

        self.round.get_small_blind(sb_i, sb)
        self.round.get_big_blind(bb_i, bb)

        self.event_manager.broadcast_to_table(
            SeatPostedSmallBlind(seat_i=self.sb_i, amount=self.sb).model_dump()
        )
        self.event_manager.broadcast_to_table(
            SeatPostedBigBlind(seat_i=self.bb_i, amount=self.bb).model_dump()
        )
        self.event_manager.broadcast_to_table(UpdatePot(total=self.pot).model_dump())
        # await asyncio.sleep(self.pause_between_rounds)

        self.proceed()

    def on_enter_preflop(self):
        self.deal_hole_cards()
        while not self.round.is_done:
            # TODO: Figure out options
            self.prompt_current_player(options=[Action.CALL, Action.RAISE, Action.FOLD])
            action_event = self.get_action_from_current_player()
            action_event = self._handle_no_action_received(action_event)
            self._broadcast_event_to_table(action_event)
        self.proceed()

    #
    # def on_enter_turn(self):
    #     # Does this need to be a new object everytime
    #     self.round = Round()
    #     # TODO: don't allow players to sit in in the middle of a hand
    #     while not self.round.is_done:
    #         # TODO: Figure out options
    #         self.prompt_current_player(options=[Action.CALL, Action.RAISE, Action.FOLD])
    #     self.proceed()
    #
    # def on_enter_river(self):
    #     pass
    #
    # def on_enter_showdown(self):
    #     pass

    def deal_hole_cards(self):
        for seat_i, seat in enumerate(self.seats):
            if seat and seat.is_sitting_in:
                cards = self.deck.draw_cards(2)
                seat.set_hole_cards(cards)
                self.event_manager.push_to_player(
                    seat_i=seat_i,
                    event=HoleCards(cards=cards).model_dump(),
                )
                # DO WE NEED
                # for other_seat_i, other_seat in enumerate(self.seats):
                #     if other_seat and other_seat_i != seat_i:
                #         self.get_seat_conn(seat_i=other_seat_i).send_json(
                #             DealFaceDownHoleCards(seat_i=seat_i).model_dump())

    def prompt_current_player(self, options):
        self.event_manager.push_to_player(
            self.round.current_seat_i, PromptAction(options=options)
        )

    def get_action_from_current_player(self):
        return self.event_manager.get_action_from_player(self.round)

    def _broadcast_event_to_table(self, action_event):
        if action_event:
            self.event_manager.broadcast_to_table(
                event=ACTION_EVENT_MAP[action_event["type"]](seat_i=self.round.current_seat_i, amount=action_event["amount"]))
        else:
            if self.round.no_action_required or self.round.current_player.chips_put_in == self.round.current_bet:
                self.event_manager.broadcast_to_table(event=CheckEvent(seat_i=self.round.current_seat_i))
            else:
                self.event_manager.broadcast_to_table(event=CheckEvent(seat_i=self.round.current_seat_i))

    def _handle_no_action_received(self, action_event):
        if not action_event:
            if self.round.no_action_required:
                if self.round.act({"type": "check"}): # TODO: This will return False with blinds pf
                    
                    return CheckEvent()
                if self.round.current_player.chips_put_in == self.round.current_bet:

                self.round
        return action_event