from players import Player
from robot import Robot
from auxfunc import check_win, ALL_MOVES


class Game:
    def __init__(self, config):
        # idkw all_moves constant becomes inaccessible or don't renew after restart if we don't calc it here
        self.available_moves = {(x, y) for x in range(0, 3) for y in range(0, 3)}
        # dealing with a leadership by letting 1st player choose his mode
        self.p1 = Player(real=True, cross=config[0])
        # dealing with a status of the remaining player
        self.p2 = Player(real=config[1], cross=not config[0])
        # this flag is used to distinguish inbetween two winners
        self.first_winner = None
        self.r = Robot(self.available_moves)
        # we'll use this flag to end our game and count draw if the winner is still None
        self.end = False

    def step(self, first_turn, click_coord):
        robo_choice = False
        if first_turn:
            curr_player = self.p1
        else:
            curr_player = self.p2
        # filter two type of possible players - real and ai
        if curr_player.role:
            curr_player.move(click_coord)
        else:
            self.r.strategy(self.p2.moves, self.available_moves)
            robo_choice = self.r.result[0]
            curr_player.move(robo_choice)
            print(self.r.result, "ROBOT!")
        # update available moves set
        try:
            self.available_moves.remove(curr_player.moves[-1])
        # unknown rare bug after game end, possibly fault mouse click event handler when I click too fast
        # sometimes robot continues to work => overlaps used points, quite hard to catch that bug
        except KeyError:
            print('bug', self.available_moves, curr_player.moves[-1], self.end)
        # stop if no available_moves left
        if len(self.available_moves) == 0:
            self.end = True
        # check for winner
        if check_win(curr_player.moves):
            self.end = True
            if curr_player == self.p1:
                self.first_winner = True
            else:
                self.first_winner = False
        return robo_choice
