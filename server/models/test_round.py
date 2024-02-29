import pytest

from models.round import Round
from models.seat import Seat


class TestRound:
    def test_new_round(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)
        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.current_player == seat_1
        assert round.current_player.chips_put_in == 0
        assert not round.is_done
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 0

    def test_no_action_key(self):
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
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 0

    def test_invalid_action_key(self):
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
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 0

    def test_check(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)
        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.act(action_event={"type": "check"})
        assert round.current_player == seat_2
        assert seat_1.chips_put_in == 0 == seat_2.chips_put_in
        assert seat_1.chips == 1000 == seat_2.chips
        assert not round.is_done
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 0

    def test_bet(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)

        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.act(action_event={"type": "bet", "amount": 10})
        assert seat_1.chips_put_in == 10
        assert seat_1.chips == 990
        assert round.current_player == seat_2
        assert round.last_bettor_i == 0
        assert not round.is_done
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 10

    def test_raise(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)

        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert not round.act(action_event={"type": "raise", "amount": 10})
        assert seat_1.chips_put_in == 0
        assert seat_1.chips == 1000
        assert round.current_player == seat_1
        assert round.last_bettor_i == 0
        assert not round.is_done
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 0

    def test_no_raise_amount_key(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)

        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.act(action_event={"type": "bet", "amount": 10})
        assert not round.act(action_event={"type": "raise"})
        assert seat_2.chips_put_in == 0
        assert seat_2.chips == 1000
        assert not round.is_done
        assert not round.everyone_has_folded
        assert not round.all_checked
        assert round.pot == 10

    def test_fold(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)

        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.act(action_event={"type": "fold", "amount": 10})
        assert seat_1.chips_put_in == 0
        assert seat_1.chips == 1000
        assert round.is_done
        assert round.everyone_has_folded
        assert round.pot == 0

    def test_check_check(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)
        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.act(action_event={"type": "check"})

        assert round.act(action_event={"type": "check"})
        assert round.all_checked
        assert round.is_done
        assert not round.everyone_has_folded
        assert round.pot == 0

    def test_check_bet(self):
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
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 10

    @pytest.mark.parametrize("bet", [9, 1001, -1, None])
    def test_invalid_bet(self, bet):
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
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 0

    def test_no_bet_amount_key(self):
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
        assert not round.all_checked
        assert not round.everyone_has_folded
        assert round.pot == 0

    def test_bet_raise(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)

        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.act(action_event={"type": "bet", "amount": 10})
        assert round.act(action_event={"type": "raise", "amount": 20})
        assert seat_2.chips_put_in == 20
        assert seat_2.chips == 980
        assert not round.is_done
        assert not round.everyone_has_folded
        assert not round.all_checked
        assert round.pot == 30

    def test_check_bet_check(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)

        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.act(action_event={"type": "check"})

        assert round.act(action_event={"type": "bet", "amount": 10})

        assert not round.act(action_event={"type": "check"})
        assert round.current_player == seat_1
        assert round.last_bettor_i == 1
        assert not round.all_checked
        assert not round.is_done
        assert not round.everyone_has_folded
        assert round.pot == 10

    def test_check_bet_fold(self):
        seat_1 = Seat(player_id="a1", chips=1000)
        seat_2 = Seat(player_id="b2", chips=1000)

        round = Round(seats=[seat_1, seat_2], first_to_act_i=0, bb=10)

        assert round.act(action_event={"type": "check"})

        assert round.act(action_event={"type": "bet", "amount": 10})

        assert round.act(action_event={"type": "fold"})
        assert round.is_done
        assert round.everyone_has_folded
        assert not round.all_checked
        assert round.pot == 10

    def test_check_bet_call(self):
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
        assert not round.all_checked
        assert round.pot == 20

    def test_check_bet_bet(self):
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
        assert not round.all_checked
        assert not round.is_done
        assert not round.everyone_has_folded
        assert round.pot == 10

    @pytest.mark.parametrize("raise_amount", [5, 1001, -1])
    def test_check_bet_invalid_raise(self, raise_amount):
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
        assert not round.all_checked
        assert not round.is_done
        assert not round.everyone_has_folded
        assert round.pot == 10

    def test_check_bet_raise(self):
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
        assert not round.all_checked
        assert round.pot == 30

    def test_check_bet_raise_call(self):
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
        assert not round.all_checked
        assert round.pot == 40

    def test_reraise(self):
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
        assert not round.all_checked
        assert round.pot == 50
        assert round.current_player == seat_2

    @pytest.mark.parametrize("reraise_amount", [-1, 29, 1001, None])
    def test_invalid_re_raise(self, reraise_amount):
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
        assert not round.all_checked
        assert round.pot == 30
