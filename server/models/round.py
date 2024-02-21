from models.table import Seat, Action, PlayerStatus


class Round:
    def __init__(self, seats, sb_i, bb_i, button_i, current_i, bb):
        self.bb = bb
        self.seats: list[Seat] = seats
        self.current_i = sb_i
        self.last_bettor = current_i
        self.current_bet = 0
        self.minimum_bet = 0
        self.has_started = False

    def act(self, action, amount=None):
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
    def round_is_done(self):
        return self.has_started and self.last_bettor == self.current_i

    @property
    def all_checked(self):
        return all(
            seat.state in (PlayerStatus.CHECK, PlayerStatus.FOLD) for seat in self.seats
        )

    @property
    def has_everyone_folded(self):
        return sum(seat.state != PlayerStatus.FOLD for seat in self.seats) == 1


    # Active Bet?

    #              -> Current: Seat 3, State: Start     None last_to_act: Seat 2
    # Seat 3 Check -> Current: Seat 4, State: Checked   None last_to_act: Seat 2
    # Seat 4 Check -> Current: Seat 5, State: Checked   None last_to_act: Seat 2
    # Seat 5 Bet   -> Current: Seat 6, State: Bet   last_to_act: Seat 4
    # Seat 6 Fold  -> Current: Seat 7, State: Bet  last_to_act: Seat 4
    # Seat 7 Call  -> Current: Seat 8, State: Bet   last_to_act: Seat 4
    # Seat 8 Raise  -> Current: Seat 1, State: Bet   last_to_act: Seat 7
    # Seat 1 Fold  ->  Current: Seat 2, State: Bet   last_to_act: Seat 7
    # Seat 2 Fold  ->  Current: Seat 3, State: Bet  last_to_act: Seat 7
    # Seat 3 Fold  ->  Current: Seat 4, State: Bet   last_to_act: Seat 7
    # Seat 4 Call  ->  Current: Seat 5, State: Bet   last_to_act: Seat 7
    # Seat 5 Fold  ->  Current: Seat 7, State: Bet   last_to_act: Seat 7
    # Seat 7 Fold  ->  Current: Seat X, State: End   last_to_act: Seat 7
