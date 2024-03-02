from phevaluator import evaluate_cards

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
    DeclareWinnerEvent,
)
from models.enums import Action
from models.seat import Seat


class Hand:
    def __init__(
        self,
        seats,
        sb,
        bb,
        sb_i,
        bb_i,
        event_manager,
        evaluator=evaluate_cards,
        pause_between_rounds=1,
    ):
        self.seats: list[Seat] = seats
        self.sb = sb
        self.bb = bb
        self.sb_i = sb_i
        self.bb_i = bb_i
        self.last_to_act = self.bb_i
        self.pause_between_rounds = pause_between_rounds
        self.pot = 0
        self.board: list[int] = []
        self.deck = Deck()
        self.event_manager = event_manager
        self.round = Round(
            seats=self.seats,
            first_to_act_i=sb_i,
            bb=self.bb,
        )
        self.evaluator = evaluator
        self.winning_seat_i = None

        # TODO: Handle not having enough players to start a hand
        # self.proceed()

    async def begin_preflop(self):
        print(f"PREFLOP STARTED !!!!!!!!!!!!")

        self.round.get_small_blind(self.sb_i, self.sb)
        self.round.get_big_blind(self.bb_i, self.bb)
        await self.event_manager.broadcast_to_table(
            SeatPostedSmallBlind(seat_i=self.sb_i, amount=self.sb).model_dump_json()
        )
        await self.event_manager.broadcast_to_table(
            SeatPostedBigBlind(seat_i=self.bb_i, amount=self.bb).model_dump_json()
        )
        await self.event_manager.broadcast_to_table(
            UpdatePot(total=self.pot).model_dump_json()
        )
        # await asyncio.sleep(self.pause_between_rounds)
        await self._deal_hole_cards()
        while not self.round.is_done:
            await self.prompt_current_player(options=self.round.actions_allowed)
            action_event = await self._get_action_from_current_player()
            action_event = self._handle_no_action_received(action_event)
            await self._broadcast_action(action_event)
        print("COLLECTING CHIPS")
        self._collect_chips()
        if self.round.everyone_has_folded:
            return self.finish_hand()
        return await self.begin_flop()

    async def begin_flop(self):
        print(f"FLOP STARTED !!!!!!!!!!!!")
        # TODO: don't allow players to sit in in the middle of a hand
        await self._deal_flop_cards()

        if self.round.players_are_all_in:
            return self.begin_turn()

        self.round = Round(seats=self.seats, first_to_act_i=self.bb_i, bb=self.bb)

        while not self.round.is_done:
            await self.prompt_current_player(options=self.round.actions_allowed)
            action_event = await self._get_action_from_current_player()
            action_event = self._handle_no_action_received(action_event)
            await self._broadcast_action(action_event)

        self._collect_chips()
        if self.round.everyone_has_folded:
            return self.finish_hand()
        return await self.begin_turn()

    async def begin_turn(self):
        print(f"TURN STARTED !!!!!!!!!!!!")
        await self._deal_turn_card()

        if self.round.players_are_all_in:
            return self.begin_river()

        self.round = Round(seats=self.seats, first_to_act_i=self.bb_i, bb=self.bb)

        while not self.round.is_done:
            await self.prompt_current_player(options=self.round.actions_allowed)
            action_event = await self._get_action_from_current_player()
            action_event = self._handle_no_action_received(action_event)
            await self._broadcast_action(action_event)

        self._collect_chips()
        if self.round.everyone_has_folded:
            return self.finish_hand()
        return await self.begin_river()

    async def begin_river(self):
        print(f"RIVER STARTED !!!!!!!!!!!!")
        await self._deal_river_card()

        if self.round.players_are_all_in:
            return self.showdown()

        self.round = Round(seats=self.seats, first_to_act_i=self.bb_i, bb=self.bb)

        while not self.round.is_done:
            await self.prompt_current_player(options=self.round.actions_allowed)
            action_event = await self._get_action_from_current_player()
            action_event = self._handle_no_action_received(action_event)
            await self._broadcast_action(action_event)

        self._collect_chips()
        if self.round.everyone_has_folded:
            return self.finish_hand()
        return await self.showdown()

    async def showdown(self):
        print(f"SHOWDOWN STARTED !!!!!!!!!!!!")
        # TODO: Give option to not flip cards and flip hole cards in order
        flipped_cards = self._flip_cards_over()

        self.winning_seat_i = self._determine_winner(flipped_cards)
        self.event_manager.broadcast_to_table(
            DeclareWinnerEvent(winning_seat_i=self.winning_seat_i).json()
        )
        return self.finish_hand()

    def finish_hand(self):
        print(f"FINISH HAND STARTED !!!!!!!!!!!!")
        if self.winning_seat_i is None and self.round.everyone_has_folded:
            self.winning_seat_i = self.round.last_man_standing_i
        self._push_winnings()

    async def prompt_current_player(self, options):
        await self.event_manager.push_to_player(
            self.round.current_seat_i, PromptAction(options=options).model_dump_json()
        )

    async def _get_action_from_current_player(self):
        return await self.event_manager.get_action_from_player(self.round)

    def _handle_no_action_received(self, action_event):
        if not action_event:
            if self.round.no_action_required:
                self.round.act({"type": Action.CHECK.value})
                return CheckEvent(seat_id=self.round.current_seat_i)
            self.round.act({"type": Action.FOLD.value})
            return FoldEvent(seat_id=self.round.current_seat_i)
        return action_event

    async def _broadcast_action(self, action_event):
        amount = action_event.get("amount")
        action_event = ACTION_EVENT_MAP[action_event["type"]](
            seat_i=self.round.current_seat_i
        )
        if amount:
            action_event.amount = amount
        await self.event_manager.broadcast_to_table(
            event=action_event.model_dump_json()
        )

    def _collect_chips(self):
        for seat in self.seats:
            seat.chips_put_in = 0
        self.pot += self.round.pot

    async def _deal_hole_cards(self):
        for seat_i, seat in enumerate(self.seats):
            if seat and seat.is_sitting_in:
                cards = self.deck.draw_cards(2)
                seat.set_hole_cards(cards)
                await self.event_manager.push_to_player(
                    seat_i=seat_i,
                    event=HoleCards(cards=cards).model_dump_json(),
                )
        # TODO: Push to other players that player received cards for animating?

    async def _deal_flop_cards(self):
        cards = self.deck.draw_cards(3)
        self.board.extend(cards)
        await self.event_manager.broadcast_to_table(DealFlopEvent(cards=cards).json())

    async def _deal_turn_card(self):
        cards = self.deck.draw_cards(1)
        self.board.extend(cards)
        await self.event_manager.broadcast_to_table(DealTurnEvent(cards=cards).json())

    async def _deal_river_card(self):
        cards = self.deck.draw_cards(1)
        self.board.extend(cards)
        await self.event_manager.broadcast_to_table(DealRiverEvent(cards=cards).json())

    def _flip_cards_over(self) -> dict:
        hole_cards_event = FlipHoleCardsEvent()

        for i in range(len(self.seats)):
            seat_i = (self.round.last_bettor_i + i) % len(self.seats)
            if self.seats[seat_i].is_sitting_in and not self.seats[seat_i].has_folded:
                hole_cards_event.seats_i.append(seat_i)
                hole_cards_event.cards.append(self.seats[seat_i].cards)

        self.event_manager.broadcast_to_table(hole_cards_event.json())

        return hole_cards_event.model_dump_json()

    def _determine_winner(self, hole_cards):
        hand_scores = {}
        # TODO: for i in range(len(hole_cards["cards"])):
        #             ~~~~~~~~~~^^^^^^^^^
        # TypeError: string indices must be integers, not 'str'
        for i in range(len(hole_cards["cards"])):

            hand_scores[hole_cards["seats_i"][i]] = self.evaluator(
                hole_cards["cards"][i]
            )
        return min(hand_scores, key=hand_scores.get)

    def _push_winnings(self):
        print(f"winning_seat_i: {self.winning_seat_i}")
        self.seats[self.winning_seat_i].chips += self.pot
