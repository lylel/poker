from enum import Enum


class Action(Enum):
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    FOLD = "fold"


class SeatStatus(Enum):
    pass


class PlayerStatus(Enum):
    INIT = "init"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    FOLD = "fold"


class RoundState:
    START = "start"
    CHECKED = "checked"
    CALLED = "called"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all-in"
    END = "end"
