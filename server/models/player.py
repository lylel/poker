class Player:
    def __init__(
        self,
        account_id,
        chips=0,
        is_sitting_in=True,
    ):
        self.account_id = account_id
        self.chips = chips
        self.is_sitting_in = is_sitting_in
