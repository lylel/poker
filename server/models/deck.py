import random

NUMBER_OF_RANKS = 13
SUIT_MAP = {0: "c", 1: "d", 2: "h", 3: "s"}
RANK_MAP = {
    0: "2",
    1: "3",
    2: "4",
    3: "5",
    4: "6",
    5: "7",
    6: "8",
    7: "9",
    8: "10",
    9: "J",
    10: "Q",
    11: "K",
    12: "A",
}


class InvalidCardIntException:
    pass


class Deck:
    def __init__(self):
        cards = [card for card in range(52)]
        random.shuffle(cards)
        self._cards = cards

    def draw_cards(self, count):
        drawn_cards = []
        for _ in range(count):
            drawn_cards.append(self._cards.pop())
        return drawn_cards

    def convert_card_to_str(self, card_int: int) -> str:
        if not -1 < card_int < 52:
            raise InvalidCardIntException

        rank = card_int % NUMBER_OF_RANKS
        suit = card_int // NUMBER_OF_RANKS
        return RANK_MAP[rank] + SUIT_MAP[suit]

    def convert_cards_to_str(self, card_ints: list[int]) -> list[str]:
        card_strs = []
        for card_int in card_ints:
            card_strs.append(self.convert_card_to_str(card_int))
        return card_strs
