import random


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
