import random
from auxfunc import *


class Robot:
    def __init__(self, all_moves):
        # as always, everything breaks if we get this set as a parameter or imported from module. idkw
        self.MOVES_SET = {(x, y) for x in range(0, 3) for y in range(0, 3)}
        # winning pattern to end the game with cand, i.e. [point1(taken), cand, point2(taken)]
        self.win = []
        # dict {cand: [[point, cand, approx_point],...],  } of effective patterns (renews at each pattern_generator run)
        self.patterns = {}
        # remaining available points (renews at each pattern_generator run)
        self.useless = set()
        # last result (renews at each strategy run)
        self.result = (None, None)

    def reset(self):
        """resets our main attributes to their defaults"""
        self.win, self.patterns, self.useless = [], {}, set()

    def backup(self):
        """local backup for our attributes"""
        return self.win, self.patterns, self.useless

    def restore(self, saved):
        """I don't want to drop those atts to defaults because one time we might need access to previous patterns"""
        self.win, self.patterns, self.useless = saved

    def pattern_generator(self, prev_moves, available_moves):
        """this generator filters out and lists potentially efficient (or even winning) linear patterns on
        available moves set based on the set of our previous moves. It goes not too far but even 1-vicinity
        of all unpopulated points for our application seems enough"""
        # technical object to distinguish far (but still valuable, used in some pattern) points from useless
        far_pattern_points = set()
        for cand in available_moves:
            # we need some ordered object to start from, let it be a list
            curr_pattern_list = []
            # let's check if there are any of our marks nearby already
            cand_vicinity_prev = get_vicinity(cand, prev_moves)[1]
            # print(cand_vicinity_prev, f"is the populated vicinity of {cand}")
            # we've got a set of points in the vicinity of candidate, let's observe that
            # instead of "if get_vicinity(cand, prev_ai_moves)[0]:", shorter line with performance gain but poss more buggy
            if cand_vicinity_prev:
                for point in cand_vicinity_prev:
                    # enough data to create a line through 2 points, then find the 3rd point on that line
                    approx_point = line_approximation(cand, point)
                    # reflex: it could be that our approx point has already been achieved, i.e. we are in the shy of win
                    # so skip everything else and proceed with our candidate to win
                    if approx_point in prev_moves:
                        self.win = [point, cand, approx_point]
                        break
                    # btw we haven't checked if it's present in the available moves (so we could use that in future) yet
                    elif approx_point in available_moves - {cand}:
                        curr_pattern = [point, cand, approx_point]
                        curr_pattern_list.append(curr_pattern)
                        far_pattern_points.add(approx_point)
                    else:
                        # even if there are points in the vicinity, approx_point couldn't fit a line <=> approx_point = None
                        # print("strange, investigate", approx_point, available_moves)
                        self.useless.add(cand)
            # we've dealt with all possible propagations through this candidate and other our points nearby, let's save
            if len(curr_pattern_list) != 0:
                self.patterns[cand] = curr_pattern_list
            else:
                # print(f"no our points nearby {cand} or patterns through those")
                # this candidate has turned out to be useless NOW, probably should be processed in 2nd turn even in future
                self.useless.add(cand)
                self.useless -= far_pattern_points
                # don't reject em! This set contains the points less likely to win with now but also our win (if it exists)!

    def strategy(self, prev_ai_moves, available_moves, opp=False):
        """find the most effective way to win or effectively interfere with an opponent"""
        prev_ai_moves = set(prev_ai_moves)
        available_moves = set(available_moves)
        if not opp:
            # each time before we run generator, we must clear the results of previous run (=reset), don't add to those
            # as we need those new results for comparator, we set up corresponding condition
            self.reset()
        self.pattern_generator(prev_ai_moves, available_moves)
        opponent_moves = self.MOVES_SET - available_moves - prev_ai_moves
        if self.win:
            # let's try to win if we can, we assume that check_win(win) = True and it seems to be like that
            choice = self.win[1]
            choice_quality = (2, 0)
        else:
            if self.patterns:
                # if we have such patterns, then we choose the max diverse one as it's harder to block by our opponent
                max_key = max(self.patterns, key=lambda k: len(self.patterns[k]))
                choice = self.patterns.get(max_key)[0][1]
                choice_quality = (1, len(self.patterns[max_key]))
            else:
                # create set of available corner points
                free_corners = {point for point in available_moves if (point[0] != 1 or point[1] != 1)}
                if (1, 1) in available_moves:
                    # try to take the best spot (in the center) first
                    choice = (1, 1)
                    choice_quality = (0, 2)
                elif free_corners:
                    # occupy free corners
                    choice = free_corners.pop()
                    choice_quality = (0, 1)
                else:
                    # just some random choice inbetween remaining moves
                    choice = random.choice(tuple(self.useless))
                    choice_quality = (0, 0)
            # feedback comparator, compare our choice with our opponent's one
            if not opp:
                # consider the very best possible choice for opponent via recursion with feedback
                # our atts will be overwritten but I don't want to change neither pattern_generator nor strategy method
                saved = self.backup()
                inter_choice, inter_quality = self.strategy(opponent_moves, available_moves, opp=True)
                self.restore(saved)
                # unless we win, prevent our opponent from that
                if inter_quality[0] == 2:
                    choice = inter_choice
                # unless we have a better choice, mess with the opponent's one
                elif inter_quality[0] > choice_quality[0]:
                    choice = inter_choice
                # in case of the same main quality types, we choose better strategy based on 2nd quality parameter
                elif inter_quality[0] in {0, 1} and inter_quality[0] == choice_quality[0]:
                    choice = inter_choice if inter_quality[1] > choice_quality[1] else choice
                # else don't change choice var
                else:
                    pass
        self.result = (choice, choice_quality)
        return self.result

# robomoves = {(0, 0),(2, 2)}
# oppomoves = {(0, 1),(1, 1)}
# r = strategy(robomoves, ALL_MOVES-oppomoves-robomoves)
# print(r)
