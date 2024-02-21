from models.hand import Hand
from models.player import Player


class TestHand:
    def test__(self):
        player_1 = Player(account_id=11, chips=100)
        player_2 = Player(account_id=22, chips=100)
        player_3 = Player(account_id=33, chips=100)
        player_4 = Player(account_id=44, chips=100)

        seats = [player_1, player_2, player_3, player_4]

        hand = Hand(seats=seats, sb=1, bb=2, sb_i=0, bb_i=1, button_i=3)
        hand.deal_holecards()
        hand.fold(player_3.account_id)
        hand.call(player_4.account_id)
        hand.call(player_1.account_id)
        hand.check(player_2.account_id)

        hand.deal_flop()
        hand.check(player_1.account_id)
        hand.check(player_2.account_id)
        hand.bet(player_4.account_id, 20)

        hand.fold(player_1.account_id)
        hand.call(player_2.account_id)

        hand.deal_turn()
        hand.check(player_2.account_id)
        hand.bet(player_4.account_id, 30)

        hand.call(player_2.account_id)

        hand.deal_river()
        hand.check(player_2.account_id)
        hand.check(player_4.account_id)

        hand.show_down()
