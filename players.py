class Player:
    def __init__(self, real=False, cross=False):
        self.role = real
        self.moves = []
        self.mode = cross
        # At first I wanted to transfer those atts as strings and eval as function name then, unused
        # if self.mode:
        #     self.fname = 'cross'
        # else:
        #     self.fname = 'zero'

    def move(self, next_move=False):
        # distinguish between real player's case and ai - don't need to deal with that anymore, moved to engine
        self.moves.append(next_move)
