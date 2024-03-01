import asyncio

from transitions import Machine

from constants import COMPLETE_BOARD_SIZE
from models.round import Round
from models.deck import Deck
from client_events.events import (
    HoleCards,
    SeatPostedSmallBlind,
    SeatPostedBigBlind,
    UpdatePot,
    PromptAction,
    ACTION_EVENT_MAP,
    CheckEvent,
    FoldEvent,
    DealFlopEvent,
    DealTurnEvent,
    DealRiverEvent,
    FlipHoleCardsEvent,
)
from models.enums import Action
from models.seat import Seat


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
            "conditions": "everyone_has_folded",
        },
        {"trigger": "proceed", "source": "flop", "dest": "turn"},
        {
            "trigger": "proceed",
            "source": "flop",
            "dest": "end",
            "conditions": "everyone_has_folded",
        },
        {"trigger": "proceed", "source": "turn", "dest": "river"},
        {
            "trigger": "proceed",
            "source": "turn",
            "dest": "end",
            "conditions": "everyone_has_folded",
        },
        {"trigger": "proceed", "source": "river", "dest": "showdown"},
        {
            "trigger": "proceed",
            "source": "river",
            "dest": "end",
            "conditions": "everyone_has_folded",
        },
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
        # TODO: Handle not having enough players to start a hand
        self.proceed()

    def on_enter_preflop(self):
        self.round.get_small_blind(self.sb_i, self.sb)
        self.round.get_big_blind(self.bb_i, self.bb)

        self.event_manager.broadcast_to_table(
            SeatPostedSmallBlind(seat_i=self.sb_i, amount=self.sb).model_dump()
        )
        self.event_manager.broadcast_to_table(
            SeatPostedBigBlind(seat_i=self.bb_i, amount=self.bb).model_dump()
        )
        self.event_manager.broadcast_to_table(UpdatePot(total=self.pot).model_dump())
        # await asyncio.sleep(self.pause_between_rounds)
        self._deal_hole_cards()
        while not self.round.is_done:
            self.prompt_current_player(options=self.round.actions_allowed)
            action_event = self._get_action_from_current_player()
            action_event = self._handle_no_action_received(action_event)
            self._broadcast_event_to_table(action_event)

        self._collect_chips()
        self.proceed()

    def on_enter_flop(self):
        # TODO: don't allow players to sit in in the middle of a hand
        self._deal_flop()

        if self.round.players_are_all_in:
            return self.proceed()

        self.round = Round(seats=self.seats, first_to_act_i=self.bb_i, bb=self.bb)

        while not self.round.is_done:
            self.prompt_current_player(options=self.round.actions_allowed)

        self._collect_chips()
        self.proceed()

    def on_enter_turn(self):
        self._deal_turn()

        if self.round.players_are_all_in:
            return self.proceed()

        self.round = Round(seats=self.seats, first_to_act_i=self.bb_i, bb=self.bb)

        while not self.round.is_done:
            self.prompt_current_player(options=self.round.actions_allowed)

        self._collect_chips()
        self.proceed()

    def on_enter_river(self):
        self._deal_river()

        if self.round.players_are_all_in:
            return self.proceed()

        self.round = Round(seats=self.seats, first_to_act_i=self.bb_i, bb=self.bb)

        while not self.round.is_done:
            self.prompt_current_player(options=self.round.actions_allowed)

        self._collect_chips()
        self.proceed()

    def on_enter_showdown(self):
        # TODO: Give option to not flip cards and flip hole cards in order
        flipped_cards = self._flip_cards_over()

        self.evaluate_winner()

    def on_enter_end(self):
        self.round.winner.chips += self.pot

    def everyone_has_folded(self):
        return self.round.everyone_has_folded

    def prompt_current_player(self, options):
        self.event_manager.push_to_player(
            self.round.current_seat_i, PromptAction(options=options)
        )

    def _get_action_from_current_player(self):
        return self.event_manager.get_action_from_player(self.round)

    def _handle_no_action_received(self, action_event):
        if not action_event:
            if self.round.no_action_required:
                self.round.act({"type": Action.CHECK.value})
                return CheckEvent(seat_id=self.round.current_seat_i)
            self.round.act({"type": Action.FOLD.value})
            return FoldEvent(seat_id=self.round.current_seat_i)
        return action_event

    def _broadcast_event_to_table(self, action_event):
        self.event_manager.broadcast_to_table(
            event=ACTION_EVENT_MAP[action_event["type"]](
                seat_i=self.round.current_seat_i,
                amount=action_event.get("amount").json(),
            )
        )

    def _collect_chips(self):
        for seat in self.seats:
            seat.chips_put_in = 0
        self.pot += self.round.pot

    def _deal_hole_cards(self):
        for seat_i, seat in enumerate(self.seats):
            if seat and seat.is_sitting_in:
                cards = self.deck.draw_cards(2)
                seat.set_hole_cards(cards)
                self.event_manager.push_to_player(
                    seat_i=seat_i,
                    event=HoleCards(cards=cards).model_dump(),
                )
        # TODO: Push to other players that player received cards for animating?

    def _deal_flop(self):
        cards = self.deck.draw_cards(3)
        self.board.extend(cards)
        self.event_manager.broadcast_to_table(DealFlopEvent(cards=cards).json())

    def _deal_turn(self):
        cards = self.deck.draw_cards(1)
        self.board.extend(cards)
        self.event_manager.broadcast_to_table(DealTurnEvent(cards=cards).json())

    def _deal_river(self):
        cards = self.deck.draw_cards(1)
        self.board.extend(cards)
        self.event_manager.broadcast_to_table(DealRiverEvent(cards=cards).json())

    def _flip_cards_over(self) -> FlipHoleCardsEvent:
        hole_cards_event = FlipHoleCardsEvent()

        for i in range(len(self.seats)):
            seat_i = (self.round.last_bettor_i + i) % len(self.seats)
            if self.seats[seat_i].is_sitting_in and not self.seats[seat_i].has_folded:
                hole_cards_event.seats_i.append(seat_i)
                hole_cards_event.cards.append(self.seats[seat_i].cards)

        self.event_manager.broadcast_to_table(hole_cards_event.json())

        return hole_cards_event
