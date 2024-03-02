from unittest.mock import MagicMock


from models.hand import Hand
from models.seat import Seat


class TestHand:
    def test___(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)
        event_manager_mock = MagicMock()
        hand = Hand(
            seats=[seat_1, seat_2],
            sb=5,
            bb=10,
            sb_i=0,
            bb_i=1,
            event_manager=event_manager_mock,
        )
        x = True
        assert True
