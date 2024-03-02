from models.deck import Deck


def test_convert_card_to_str():
    deck = Deck()
    assert deck.convert_card_to_str(0) == "2c"
    assert deck.convert_card_to_str(1) == "3c"
    assert deck.convert_card_to_str(2) == "4c"
    assert deck.convert_card_to_str(3) == "5c"
    assert deck.convert_card_to_str(48) == "Js"
    assert deck.convert_card_to_str(49) == "Qs"
    assert deck.convert_card_to_str(50) == "Ks"
    assert deck.convert_card_to_str(51) == "As"

    for card_int, expected_str in enumerate(
        [
            "2c",
            "3c",
            "4c",
            "5c",
            "6c",
            "7c",
            "8c",
            "9c",
            "10c",
            "Jc",
            "Qc",
            "Kc",
            "Ac",
            "2d",
            "3d",
            "4d",
            "5d",
            "6d",
            "7d",
            "8d",
            "9d",
            "10d",
            "Jd",
            "Qd",
            "Kd",
            "Ad",
            "2h",
            "3h",
            "4h",
            "5h",
            "6h",
            "7h",
            "8h",
            "9h",
            "10h",
            "Jh",
            "Qh",
            "Kh",
            "Ah",
            "2s",
            "3s",
            "4s",
            "5s",
            "6s",
            "7s",
            "8s",
            "9s",
            "10s",
            "Js",
            "Qs",
            "Ks",
            "As",
        ]
    ):
        assert deck.convert_card_to_str(card_int) == expected_str


def test_convert_cards_to_str():
    test_cases = [
        # Case 1: Different suits and ranks
        ([0, 13, 26, 39, 4, 17, 30], ["2c", "2d", "2h", "2s", "6c", "6d", "6h"]),
        ([2, 15, 28, 41, 6, 19, 50], ["4c", "4d", "4h", "4s", "8c", "8d", "Ks"]),
        # Case 3: Random mix of cards
        ([8, 22, 36, 50, 11, 25, 38], ["10c", "Jd", "Qh", "Ks", "Kc", "Ad", "Ah"]),
        # Case 4: All Aces
        ([12, 25, 38, 51, 0, 13, 26], ["Ac", "Ad", "Ah", "As", "2c", "2d", "2h"]),
        # Case 5: All 10s with different suits
        ([8, 21, 34, 47, 10, 23, 36], ["10c", "10d", "10h", "10s", "Qc", "Qd", "Qh"]),
        # Case 6: All face cards with different suits
        ([9, 22, 35, 48, 11, 24, 37], ["Jc", "Jd", "Jh", "Js", "Kc", "Kd", "Kh"]),
        # Case 7: All 2s with different suits
        ([0, 13, 26, 39, 49, 51, 50], ["2c", "2d", "2h", "2s", "Qs", "As", "Ks"]),
    ]

    d = Deck()
    for test_case in test_cases:
        assert d.convert_cards_to_str(test_case[0]) == test_case[1]
