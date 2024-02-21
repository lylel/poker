from models.table import Table
from models.player import Player


def test__table():
    player_1 = Player(account_id=1, chips=1000)
    player_2 = Player(account_id=2, chips=1000)

    seats = [player_1, player_2]

    table = Table(name="Arctic", max_seats=2, sb=1, bb=2)

    table.sit_player(player=player_1, seat=1)
    table.sit_player(player=player_2, seat=2)

    table.new_hand(sb_i=0, bb_i=1)
    table.post_small_blind(player_1.account_id)
    table.post_big_blind(player_2.account_id)

    table.check(player_2.account_id)
    table.check(player_1.account_id)

    table.check(player_2.account_id)
    table.bet(player_1.account_id, 3)
    table.call(player_2.account_id)

    table.bet(player_2.account_id, 7)
    table.fold(player_1.account_id)


