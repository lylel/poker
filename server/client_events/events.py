from pydantic import BaseModel

from models.enums import Action
from models.seat import Seat


# class TableStateRefreshEvent(BaseModel):
#     seats: list[Seat]


class HoleCards(BaseModel):
    name: str = "holeCards"
    cards: list[int]


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


class CheckEvent(BaseModel):
    name: str = "checkEvent"
    seat_i: int
    table_id: str  # TODO: is this needed?


class FoldEvent(BaseModel):
    name: str = "foldEvent"
    seat_i: int
    table_id: str  # TODO: is this needed?


ACTION_EVENT_MAP = {}
