import pytest

from models.round import Round
from models.seat import Seat


def test_new_round():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)
    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.current_player == seat_1
    assert round.current_player.chips_put_in == 0
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 0


def test_no_action_key():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert not round.act(action_event={})
    assert seat_1.chips_put_in == 0 == seat_2.chips_put_in
    assert seat_1.chips == 1000 == seat_2.chips

    assert round.current_player == seat_1
    assert round.last_bettor_i == 0
    assert not round.has_started
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 0


def test_invalid_action_key():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert not round.act(action_event={"type": "bullshit"})
    assert seat_1.chips_put_in == 0 == seat_2.chips_put_in
    assert seat_1.chips == 1000 == seat_2.chips
    assert round.current_player == seat_1
    assert round.last_bettor_i == 0
    assert not round.has_started
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 0


def test_check():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)
    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})
    assert round.current_player == seat_2
    assert seat_1.chips_put_in == 0 == seat_2.chips_put_in
    assert seat_1.chips == 1000 == seat_2.chips
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 0


def test_bet():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "bet", "amount": 10})
    assert seat_1.chips_put_in == 10
    assert seat_1.chips == 990
    assert round.current_player == seat_2
    assert round.last_bettor_i == 0
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 10


def test_raise():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert not round.act(action_event={"type": "raise", "amount": 10})
    assert seat_1.chips_put_in == 0
    assert seat_1.chips == 1000
    assert round.current_player == seat_1
    assert round.last_bettor_i == 0
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 0


def test_no_raise_amount_key():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "bet", "amount": 10})
    assert not round.act(action_event={"type": "raise"})
    assert seat_2.chips_put_in == 0
    assert seat_2.chips == 1000
    assert not round.is_done
    assert not round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 10


def test_fold():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "fold", "amount": 10})
    assert seat_1.chips_put_in == 0
    assert seat_1.chips == 1000
    assert round.is_done
    assert round.everyone_has_folded
    assert round.pot == 0


def test_check_check():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)
    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "check"})
    assert round.no_action_required
    assert round.is_done
    assert not round.everyone_has_folded
    assert round.pot == 0


def test_check_bet():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "bet", "amount": 10})
    assert seat_2.chips_put_in == 10
    assert seat_2.chips == 990
    assert round.current_player == seat_1
    assert round.last_bettor_i == 1
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 10


@pytest.mark.parametrize("bet", [9, 1001, -1, None])
def test_invalid_bet(bet):
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert not round.act(action_event={"type": "bet", "amount": bet})
    assert seat_1.chips_put_in == 0
    assert seat_1.chips == 1000
    assert round.current_player == seat_1
    assert round.last_bettor_i == 0
    assert not round.has_started
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 0


def test_no_bet_amount_key():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert not round.act(action_event={"type": "bet"})
    assert seat_1.chips_put_in == 0
    assert seat_1.chips == 1000
    assert round.current_player == seat_1
    assert round.last_bettor_i == 0
    assert not round.has_started
    assert not round.is_done
    assert not round.no_action_required
    assert not round.everyone_has_folded
    assert round.pot == 0


def test_bet_raise():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "bet", "amount": 10})
    assert round.act(action_event={"type": "raise", "amount": 20})
    assert seat_2.chips_put_in == 20
    assert seat_2.chips == 980
    assert not round.is_done
    assert not round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 30


def test_check_bet_check():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert not round.act(action_event={"type": "check"})
    assert round.current_player == seat_1
    assert round.last_bettor_i == 1
    assert not round.no_action_required
    assert not round.is_done
    assert not round.everyone_has_folded
    assert round.pot == 10


def test_check_bet_fold():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert round.act(action_event={"type": "fold"})
    assert round.is_done
    assert round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 10


def test_check_bet_call():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert round.act(action_event={"type": "call"})
    assert seat_2.chips_put_in == 10
    assert seat_2.chips == 990
    assert round.is_done
    assert not round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 20


def test_check_bet_bet():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert not round.act(action_event={"type": "bet", "amount": 30})
    assert seat_1.chips_put_in == 0
    assert seat_1.chips == 1000
    assert round.current_player == seat_1
    assert round.last_bettor_i == 1
    assert not round.no_action_required
    assert not round.is_done
    assert not round.everyone_has_folded
    assert round.pot == 10


@pytest.mark.parametrize("raise_amount", [5, 1001, -1])
def test_check_bet_invalid_raise(raise_amount):
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert not round.act(action_event={"type": "raise", "amount": raise_amount})
    assert seat_1.chips_put_in == 0
    assert seat_1.chips == 1000
    assert round.current_player == seat_1
    assert round.last_bettor_i == 1
    assert not round.no_action_required
    assert not round.is_done
    assert not round.everyone_has_folded
    assert round.pot == 10


def test_check_bet_raise():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert round.act(action_event={"type": "raise", "amount": 20})
    assert seat_1.chips_put_in == 20
    assert seat_1.chips == 980
    assert not round.is_done
    assert not round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 30


def test_check_bet_raise_call():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "check"})

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert round.act(action_event={"type": "raise", "amount": 20})

    assert round.act(action_event={"type": "call"})
    assert seat_2.chips_put_in == 20
    assert seat_2.chips == 980
    assert round.is_done
    assert not round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 40


def test_reraise():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert round.act(action_event={"type": "raise", "amount": 20})

    assert round.act(action_event={"type": "raise", "amount": 30})

    assert seat_1.chips_put_in == 30
    assert seat_1.chips == 970
    assert not round.is_done
    assert not round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 50
    assert round.current_player == seat_2


def test_reraise_call():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert round.act(action_event={"type": "raise", "amount": 20})

    assert round.act(action_event={"type": "raise", "amount": 30})

    assert round.act(action_event={"type": "call"})

    assert seat_1.chips_put_in == seat_2.chips_put_in == 30
    assert seat_1.chips == seat_2.chips == 970
    assert round.is_done
    assert not round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 60


def test_reraise_fold():
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert round.act(action_event={"type": "raise", "amount": 20})

    assert round.act(action_event={"type": "raise", "amount": 30})

    assert round.act(action_event={"type": "fold"})

    assert seat_1.chips_put_in == 30
    assert seat_2.chips_put_in == 20
    assert seat_1.chips == 970
    assert seat_2.chips == 980
    assert round.is_done
    assert round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 50


@pytest.mark.parametrize("reraise_amount", [-1, 29, 1001, None])
def test_invalid_re_raise(reraise_amount):
    seat_1 = Seat(player_id="a1", chips=1000)
    seat_2 = Seat(player_id="b2", chips=1000)

    round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

    assert round.act(action_event={"type": "bet", "amount": 10})

    assert round.act(action_event={"type": "raise", "amount": 20})

    assert not round.act(action_event={"type": "raise", "amount": reraise_amount})

    assert seat_1.chips_put_in == 10
    assert seat_1.chips == 990
    assert not round.is_done
    assert not round.everyone_has_folded
    assert not round.no_action_required
    assert round.pot == 30
