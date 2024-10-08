from pydantic import BaseModel

from models.enums import Action
from models.seat import Seat


# class TableStateRefreshEvent(BaseModel):
#     seats: list[Seat]


class HoleCards(BaseModel):
    name: str = "holeCards"
    cards: list[str]


class DealFaceDownHoleCards(BaseModel):
    name: str = "dealFaceDownHoleCards"
    seat_i: int


class SeatPostedSmallBlind(BaseModel):
    name: str = "seatPostedSmallBlind"
    seat_i: int
    amount: int


class SeatPostedBigBlind(BaseModel):
    name: str = "seatPostedBigBlind"
    seat_i: int
    amount: int


class UpdatePot(BaseModel):
    name: str = "updatePot"
    total: int


class PromptAction(BaseModel):
    name: str = "promptAction"
    options: list[Action]


class InvalidActionSubmittedEvent(BaseModel):
    name: str = "InvalidActionSubmittedEvent"


class FlipHoleCardsEvent(BaseModel):
    name: str = "flipHoleCardsEvent"
    seats_i: list[int] = []
    cards: list[list[str]] = []


class DealFlopEvent(BaseModel):
    name: str = "dealFlopEvent"
    cards: list[str]


class DealTurnEvent(BaseModel):
    name: str = "dealTurnEvent"
    cards: list[str]


class DealRiverEvent(BaseModel):
    name: str = "dealRiverEvent"
    cards: list[str]


class CheckEvent(BaseModel):
    name: str = "checkEvent"
    seat_i: int


class FoldEvent(BaseModel):
    name: str = "foldEvent"
    seat_i: int


class BetEvent(BaseModel):
    name: str = "betEvent"
    seat_i: int
    amount: int


class CallEvent(BaseModel):
    name: str = "callEvent"
    seat_i: int


class RaiseEvent(BaseModel):
    name: str = "raiseEvent"
    seat_i: int
    amount: int


class DeclareWinnersEvent(BaseModel):
    name: str = "declareWinnersEvent"
    winning_seats_i: list[int]


# TODO: AllInEvent

ACTION_EVENT_MAP = {
    Action.CHECK.value: CheckEvent,
    Action.BET.value: BetEvent,
    Action.CALL.value: CallEvent,
    Action.FOLD.value: FoldEvent,
    Action.RAISE.value: RaiseEvent,
}
