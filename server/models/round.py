from models.table import Action, PlayerStatus


class Round:
    def __init__(self, seats, sb_i, bb_i, button_i, current_i, bb):
        self.bb = bb
        self.seats: list[Seat] = seats
        self.current_i = sb_i
        self.last_bettor = current_i
        self.current_bet = 0
        self.minimum_bet = 0
        self.has_started = False

    def act(self, action_event):
        action, amount = action_event["type"], action_event["amount"]
        if action == Action.CHECK:
            if self.current_bet == 0:
                self.seats[self.current_i].state = PlayerStatus.CHECK
            else:
                return False
        elif action == Action.CALL:
            self.seats[self.current_i].bet = self.current_bet
            self.seats[self.current_i].state = PlayerStatus.CALL

        elif action == Action.BET:
            if not amount:
                return False
            if self.current_bet == 0:
                if amount < self.bb:
                    return False
                self.current_bet = amount
                self.minimum_bet = amount
                self.seats[self.current_i].state = PlayerStatus.BET
                self.seats[self.current_i].bet = self.current_bet
                self.last_bettor = self.current_i

            else:
                return False
        elif action == Action.RAISE:
            if self.current_bet != 0:
                if amount < self.minimum_bet:
                    return False
                # TODO: Figure out min raise
                self.minimum_bet = amount
                self.current_bet += amount
                self.seats[self.current_i].bet = self.current_bet
                self.seats[self.current_i].state = PlayerStatus.RAISE
                self.last_bettor = self.current_i
            return False
        elif action == Action.FOLD:
            self.seats[self.current_i].state = PlayerStatus.FOLD

        self.next_player()
        self.has_started = True
        return True

    def next_player(self):
        self.current_i = (self.current_i + 1) % len(self.seats)
        while self.seats[self.current_i].state == PlayerStatus.FOLD:
            self.current_i = (self.current_i + 1) % len(self.seats)

    @property
    def is_done(self):
        return self.has_started and self.last_bettor == self.current_i

    @property
    def all_checked(self):
        # TODO: Handle Case: Preflop, everyone has called
        return all(
            seat.state in (PlayerStatus.CHECK, PlayerStatus.FOLD) for seat in self.seats
        )

    @property
    def has_everyone_folded(self):
        return sum(seat.state != PlayerStatus.FOLD for seat in self.seats) == 1


class Seat:
    def __init__(self):
        self.state = PlayerStatus.INIT
        self.bet = 0
        self.raises = []

    def __repr__(self):
        return f"State: {self.state}, Bet: {self.bet}"
