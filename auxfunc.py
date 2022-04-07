from collections import Counter

def check_win(moves):
    # idea is to check winning conditions but don't just list all winning combinations
    cr = (3 in Counter([move[0] for move in moves]).values())
    cc = (3 in Counter([move[1] for move in moves]).values())
    # two diagonals left to check
    cd = (sum(Counter([move[0] for move in moves if move[0] == move[1]]).values()) == 3)
    cad = (sum(Counter([move[0] for move in moves if move[0] == abs(move[1] - 2)]).values()) == 3)
    if cr or cc or cd or cad:
        return True
    else:
        return False

# generate set/list of 9 possible moves - unreachable if we state it here for unknown reason
ALL_MOVES = {(x, y) for x in range(0, 3) for y in range(0, 3)}

# set of possible coordinates (on one axis)
BASE_SET = {int_num for int_num in range(0, 3)}


def dist2(a, b):
    return (a[0]-b[0])**2+(a[1]-b[1])**2


def distant_subset(points):
    result = [[], 0]
    for pt1 in points:
        for pt2 in set(points) - {pt1}:
            test_dist = dist2(pt1, pt2)
            result = [[pt1, pt2], test_dist] if test_dist > result[1] else result
    return result


def addon_calc(points):
    """for each point in points we find addon which will be helpful to cross out its whole cell"""
    addons = {}
    diffx = diffy = 0
    for point in points:
        base_set = [-1, 0, 1]
        ax = base_set[point[0]]
        ay = base_set[point[1]]
        addons[point] = (ax, ay)
        diffx = ax - diffx
        diffy = ay - diffy
    if not diffx:
        # x border case
        for pt in points:
            addons[pt] = (0, addons[pt][1])
    elif not diffy:
        # y - border case
        for pt in points:
            addons[pt] = (addons[pt][0], 0)
    return addons


def get_vicinity(point, gset):
    """provides a set of points in gset close to the point (not included itself!)"""
    vic_set = set()
    # let's prepare a flag just in case, to evade counting len(vic_set) in future
    nonempty_flag = False
    for pt in gset:
        metrics = (dist2(pt, point) <= 2) and (dist2(pt, point) >= 1)
        if metrics:
            vic_set.add(pt)
            nonempty_flag = True
    # print(vic_set, f"is the populated vicinity of {point}")
    return nonempty_flag, vic_set


def line(a, b, c=False):
    """given 3 points, it calculates the line through a, b and tests if point c (if present) lies on that line"""
    slope = (a[1] - b[1]) / (a[0] - b[0])
    intercept = a[1] - slope * a[0]
    on_line = False
    if c:
        on_line = (c[1] == slope * c[0] + intercept)
    return slope, intercept, on_line


def line_approximation(a, b):
    """given 2 points, it looks for a point which lies on that line (within our field, thanks to BASE_SET constant)"""
    appr_x = appr_y = None
    # deal with the vertical lines first
    if a[0] == b[0]:
        appr_x = a[0]
        appr_y = (BASE_SET - {a[1], b[1]}).pop()
    # deal with the horizontal lines next
    elif a[1] == b[1]:
        appr_x = (BASE_SET - {a[0], b[0]}).pop()
        appr_y = a[1]
    # we have two diagonals left
    else:
        # for 3x3 field there is no other options, we'll handle both diags at once by simple elimination procedure
        pre_appr_x = (BASE_SET - {a[0], b[0]}).pop()
        pre_appr_y = (BASE_SET - {a[1], b[1]}).pop()
        # due to that simplification, it could be that the point doesn't belong to the line of the previous two
        # maybe I should find a better way to test it but anyway, this works
        if line(a, b, (pre_appr_x, pre_appr_y))[2]:
            appr_x, appr_y = pre_appr_x, pre_appr_y
        else:
            print(pre_appr_x, pre_appr_y, "is not on line", a, b)
    return appr_x, appr_y


def update(new_record):
    """this function creates or updates file with a top player's score"""
    try:
        file = open("last_score.txt", 'r')
    except FileNotFoundError:
        file = open("last_score.txt", 'w')
    finally:
        file.close()
    with open("last_score.txt", 'w') as file:
        try:
            prev_record = int(file.readline())
        except ValueError:
            prev_record = 0
        if new_record > prev_record:
            file.write(f"{new_record}")
    return prev_record
