from models.enums import Action, PlayerStatus
from models.seat import Seat


class Round:
    def __init__(self, seats, first_to_act_i, bb, require_blinds=False):
        self.bb = bb
        self.seats: list[Seat] = seats
        self.current_i = first_to_act_i
        self.last_bettor_i = first_to_act_i
        self.has_started = False
        self.current_bet = 0
        self.minimum_raise_allowed = 0
        self.require_blinds = require_blinds

    @property
    def action_map(self):
        return {
            Action.CHECK.value: self.check,
            Action.BET.value: self.bet,
            Action.CALL.value: self.call,
            Action.RAISE.value: self.raise_,
            Action.FOLD.value: self.fold,
        }

    @property
    def pot(self):
        return sum(seat.chips_put_in for seat in self.seats)

    @property
    def current_player(self):
        return self.seats[self.current_i]

    @property
    def is_done(self):
        return self.everyone_has_folded or self.has_started and self.last_bettor_i == self.current_i

    @property
    def all_checked(self):
        # TODO: Handle Case: Preflop, everyone has called
        return all(
            seat.state in (PlayerStatus.CHECK, PlayerStatus.FOLD) for seat in self.seats
        )

    @property
    def everyone_has_folded(self):
        return sum(seat.state != PlayerStatus.FOLD for seat in self.seats) == 1

    def act(self, action_event):
        if not (action := action_event.get("type")) or action not in self.action_map:
            return False

        amount = action_event.get("amount")
        if self.action_map[action](amount=amount):
            self.has_started = True
            self.set_next_player()
            return True
        return False

    def check(self, **kwargs):
        if not self.current_bet:
            self.current_player.state = PlayerStatus.CHECK
            return True
        return False

    def bet(self, **kwargs):
        amount = kwargs["amount"]
        if not amount or amount < self.bb or amount > self.current_player.chips:
            return False

        if not self.current_bet:
            self.current_bet = self.minimum_raise_allowed = (
                self.current_player.chips_put_in
            ) = amount
            self.current_player.chips -= amount
            self.last_bettor_i = self.current_i
            return True
        return False

    def call(self, **kwargs):
        if self._amount_to_call < self.current_player.chips:
            self.current_player.chips -= self._amount_to_call
            self.current_player.chips_put_in = self.current_bet
            return True
        return False

    def raise_(self, **kwargs):
        if not (total_put_in := kwargs.get("amount")):
            return False

        amount_raised = total_put_in - self.current_bet
        amount_needed_to_put_in = total_put_in - self.current_player.chips_put_in

        # TODO: How to handle all-in raise that is smaller than min raise. e.g. BB: 10, Bet 10, Raise all-in 15
        if (
            not self.current_bet
            or not total_put_in
            or amount_raised < self.minimum_raise_allowed
            or amount_needed_to_put_in > self.current_player.chips
        ):
            return False

        self.minimum_raise_allowed = amount_raised

        self.current_player.chips -= amount_needed_to_put_in
        self.current_player.chips_put_in = total_put_in
        self.current_bet = total_put_in

        self.last_bettor_i = self.current_i
        return True

    def fold(self, **kwargs):
        self.current_player.state = PlayerStatus.FOLD
        return True

    def set_next_player(self):
        self.current_i = (self.current_i + 1) % len(self.seats)
        while (
            not self.everyone_has_folded
            and self.current_player.state == PlayerStatus.FOLD
        ):
            self.current_i = (self.current_i + 1) % len(self.seats)

    @property
    def _amount_to_call(self):
        return self.current_bet - self.current_player.chips_put_in
