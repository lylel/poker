from models.enums import Action, PlayerStatus
from models.seat import Seat


class NoRemainingPlayerFoundException:
    pass


class Round:
    def __init__(self, seats, first_to_act_i, bb):
        self.seats: list[Seat | None] = seats
        self.current_seat_i = first_to_act_i
        self.last_bettor_i = first_to_act_i
        self.has_started = False
        self.current_bet = 0
        self.minimum_raise_allowed = bb

        # TODO: Check if enough players to start
        if (
            not self.current_player
            or not self.current_player.is_sitting_in
            or self.current_player.has_folded
        ):
            self.set_next_player()
            self.last_bettor_i = self.current_seat_i

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
        return self.seats[self.current_seat_i]

    @property
    def is_done(self):
        return (
            self.everyone_has_folded
            or self.has_started
            and self.last_bettor_i == self.current_seat_i
        )

    @property
    def actions_allowed(self):
        options = [Action.FOLD.value]
        if self.no_action_required:
            options.extend([Action.CHECK.value, Action.BET.value])
        if self._player_has_not_called:
            options.extend([Action.CALL.value, Action.RAISE.value])

        return options

    @property
    def no_action_required(self):
        return not self.current_bet or self._current_player_has_called

    @property
    def everyone_has_folded(self):
        has_folded = (
            sum(seat.is_sitting_in and not seat.has_folded for seat in self.seats) == 1
        )
        return has_folded

    @property
    def players_are_all_in(self):
        return sum(seat.chips > 0 and seat.is_sitting_in for seat in self.seats) <= 1

    @property
    def last_man_standing_i(self):
        if self.everyone_has_folded:
            for seat_i, seat in enumerate(self.seats):
                if seat.is_sitting_in and not seat.has_folded:
                    return seat_i
        raise NoRemainingPlayerFoundException

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
        if not self.current_bet or self._current_player_has_called:
            self.current_player.state = PlayerStatus.CHECK.value
            return True
        return False

    def bet(self, **kwargs):
        amount = kwargs["amount"]
        if (
            not amount
            or amount < self.minimum_raise_allowed
            or amount > self.current_player.chips
        ):
            return False

        if not self.current_bet:
            self.current_bet = self.minimum_raise_allowed = (
                self.current_player.chips_put_in
            ) = amount
            self.current_player.chips -= amount
            self.last_bettor_i = self.current_seat_i
            return True
        return False

    def call(self, **kwargs):
        if not self.current_bet:
            return False
        # TODO: Handle calling when not enough chips
        if self._amount_to_call > self.current_player.chips:
            self.current_player.chips_put_in += self.current_player.chips
            self.current_player.chips = 0
            # TODO: Handle more logic for > 2 players
            self.seats[self.last_bettor_i].chips += (
                self.current_bet - self.current_player.chips_put_in
            )
            self.current_bet = self.current_player.chips_put_in
            return True
        else:
            self.current_player.chips -= self._amount_to_call
            self.current_player.chips_put_in += self._amount_to_call
            return True

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

        self.last_bettor_i = self.current_seat_i
        return True

    def fold(self, **kwargs):
        self.current_player.has_folded = True
        return True

    def get_small_blind(self, sb_i, sb):
        self.seats[sb_i].chips -= sb
        self.seats[sb_i].chips_put_in = sb

    def get_big_blind(self, bb_i, bb):
        self.seats[bb_i].chips -= bb
        self.seats[bb_i].chips_put_in = bb
        self.current_bet = bb

    def set_next_player(self):
        self.current_seat_i = (self.current_seat_i + 1) % len(self.seats)
        while not self.everyone_has_folded and self.current_player.has_folded:
            self.current_seat_i = (self.current_seat_i + 1) % len(self.seats)
            print(f"CURRENT SEAT ID: {self.current_seat_i}")

    @property
    def _amount_to_call(self):
        return self.current_bet - self.current_player.chips_put_in

    @property
    def _current_player_has_called(self):
        return self.current_bet and self.current_player.chips_put_in == self.current_bet

    @property
    def _player_has_not_called(self):
        return self.current_player.chips_put_in < self.current_bet

    def __str__(self):
        repr = f"Pot: {self.pot}\n"
        for seat in self.seats:
            if seat:
                repr += f"Player ID: {seat.player_id} Chips: {seat.chips} Sitting In: {seat.is_sitting_in} Folded: {seat.has_folded} Put in: {seat.chips_put_in} \n"
        return repr
