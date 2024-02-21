from transitions import Machine


class Hand:
    states = [
        "Init",
        "Preflop",
        "Preflop_Betting",
        "Flop",
        "Turn",
        "Flop_Betting",
        "Turn_Betting",
        "River",
        "River_Betting",
        "Showdown",
        "End",
    ]

    transitions = [
        {"trigger": "proceed", "source": "End", "dest": "Init"},
        {"trigger": "proceed", "source": "Init", "dest": "Preflop"},
        {"trigger": "proceed", "source": "Preflop", "dest": "Preflop_Betting"},
        {
            "trigger": "proceed",
            "source": "Preflop",
            "dest": "End",
            "condition": "is_only_one_left",
        },
        {"trigger": "proceed", "source": "Preflop_Betting", "dest": "Flop"},
        {"trigger": "proceed", "source": "Flop", "dest": "Flop_Betting"},
        {"trigger": "proceed", "source": "Flop_Betting", "dest": "Turn"},
        {"trigger": "proceed", "source": "Turn", "dest": "Turn_Betting"},
        {"trigger": "proceed", "source": "Turn_Betting", "dest": "River"},
        {"trigger": "proceed", "source": "River", "dest": "River_Betting"},
        {"trigger": "proceed", "source": "River_Betting", "dest": "Showdown"},
        {"trigger": "proceed", "source": "Showdown", "dest": "End"},
    ]

    def __init__(self, seats, sb, bb, sb_i, bb_i, button_i):
        self.is_done = False
        self.bb = bb
        self.sb = sb
        self.seats = seats
        self.sb_i = sb_i
        self.bb_i = bb_i
        self.current_player = None
        self.live_round = None
        self.last_to_act = button_i
        self.pot = 0
        self.bets = []
        self.board = []
        self.current_betting_round = 0

        self.machine = Machine(
            model=self, states=Hand.states, transitions=Hand.transitions, initial="End"
        )

    @property
    def is_heads_up(self):
        return [player.is_sitting_in for player in self.seats] == len(2)

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
            print(f"Ended Betting Round {self.current_betting_round}")
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
