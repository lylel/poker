from pydantic import BaseModel

from models.table import Action


class HoleCards(BaseModel):
    name: str = "holeCards"
    cards: list[str]


class DealFaceDownHoleCards(BaseModel):
    name: str = "dealFaceDownHoleCards"
    seat_i: int


class PostSmallBlind(BaseModel):
    name: str = "postSmallBlind"
    seat_i: int
    amount: int


class PostBigBlind(BaseModel):
    name: str = "postBigBlind"
    seat_i: int
    amount: int


class UpdatePot(BaseModel):
    name: str = "updatePot"
    total: int


class PromptAction(BaseModel):
    name: str = "promptAction"
    options: list[Action]

