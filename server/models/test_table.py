from models.table import Table
from models.player import Player


def test__table():
    player_1 = Player(account_id=1, chips=1000)
    player_2 = Player(account_id=2, chips=1000)

    # seats = [player_1, player_2]

    table = Table(name="Arctic", max_seats=2, sb=1, bb=2)

    assert not table.sit_player_down(player_id=player_1.account_id, seat_i=2, chips=200)

    assert table.sit_player_down(player_id=player_1.account_id, seat_i=0, chips=200)
    assert table.seats[0].player_id == player_1.account_id

    assert not table.sit_player_down(player_id=player_2.account_id, seat_i=0, chips=300)
    assert table.sit_player_down(player_id=player_2.account_id, seat_i=1, chips=300)

    assert table.seats[1].player_id == player_2.account_id
    assert table.seats[0].player_id == player_1.account_id
    assert table.seats[0].chips == 200
    assert table.seats[1].chips == 300

    assert table.unseat_player(player_id=player_2.account_id)
    assert table.seats[1] is None
    assert table.unseat_player(player_id=player_2.account_id) is False

    assert table.unseat_player(player_id=player_1.account_id)
    assert table.seats[0] is None
    assert table.unseat_player(player_id=player_1.account_id) is False

    #
    # table.new_hand(sb_i=0, bb_i=1)
    # table.post_small_blind(player_1.account_id)
    # table.post_big_blind(player_2.account_id)
    #
    # table.check(player_2.account_id)
    # table.check(player_1.account_id)
    #
    # table.check(player_2.account_id)
    # table.bet(player_1.account_id, 3)
    # table.call(player_2.account_id)
    #
    # table.bet(player_2.account_id, 7)
    # table.fold(player_1.account_id)
    #
    #
