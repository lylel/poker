from models.table import Action
from models.round import Round, Seat


class TestRound:
    def test__(self):
        seats = [Seat(), Seat(), Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.BET, amount=10)  # 4
        round.act(action=Action.CALL)  # 5
        round.act(action=Action.FOLD)  # 6
        round.act(action=Action.RAISE, amount=20)  # 1
        round.act(action=Action.FOLD)  # 2

        round.act(action=Action.CALL)  # 3
        round.act(action=Action.CALL)  # 4
        round.act(action=Action.FOLD)  # 5

        x = True
        assert True

    def test__all_folded(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.BET, amount=10)  # 4
        round.act(action=Action.FOLD, amount=20)  # 1
        round.act(action=Action.FOLD)  # 2

        round.act(action=Action.FOLD)  # 3

        assert round.has_everyone_folded

    def test__not_all_folded(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.BET, amount=10)  # 4
        round.act(action=Action.FOLD, amount=20)  # 1
        round.act(action=Action.FOLD)  # 2

        round.act(action=Action.CALL)  # 3

        assert not round.has_everyone_folded

    def test__round_is_done(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.BET, amount=10)  # 4
        round.act(action=Action.FOLD, amount=20)  # 1
        round.act(action=Action.FOLD)  # 2

        round.act(action=Action.FOLD)  # 3

        assert round.round_is_done

    def test__round_is_done_1(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.BET, amount=10)  # 4
        round.act(action=Action.FOLD, amount=20)  # 1
        round.act(action=Action.FOLD)  # 2

        round.act(action=Action.CALL)  # 3

        assert round.round_is_done

    def test__round_is_done_2(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.BET, amount=10)  # Player 3
        round.act(action=Action.FOLD)  # 4
        round.act(action=Action.FOLD)  # 1
        round.act(action=Action.FOLD)  # 2

        assert round.round_is_done

    def test__round_is_done_3(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.CHECK)  # 4
        round.act(action=Action.CHECK)  # 1
        round.act(action=Action.CHECK)  # 2

        assert round.round_is_done

    def test__round_is_not_done(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.BET, amount=10)  # 4
        round.act(action=Action.FOLD, amount=20)  # 1
        round.act(action=Action.FOLD)  # 2

        assert not round.round_is_done

    def test__round_is_not_done_2(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.BET, amount=10)  # 4

        assert not round.round_is_done

    def test__round_is_not_done_3(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        assert not round.round_is_done

    def test__round_is_not_done_4(self):
        seats = [Seat(), Seat(), Seat(), Seat()]

        round = Round(seats=seats, sb_i=2, bb_i=3, button_i=1, current_i=2, bb=5)

        round.act(action=Action.CHECK)  # Player 3
        round.act(action=Action.CHECK)  # 4
        round.act(action=Action.CHECK)  # 1
        round.act(action=Action.BET)  # 2

        assert not round.round_is_done
