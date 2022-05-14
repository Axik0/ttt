from tkinter import *
from engine import Game
from auxfunc import line_approximation, update, distant_subset, addon_calc
from PIL import Image, ImageTk

# set the globals somehow for technical needs (none for simplicity reason only)
output_coord, curr_sign, skip_flag, available_moves = None, None, None, []
# these vars keep track of scores shown on the scoreboard
count_O, count_X, max_score = 0, 0, update(0)


def visualiser(func):
    """catches mouse click and current global sign var state to draw cross or zero """
    def wrapper(*args):
        # we have to run everything else before our code to get output coordinates
        func(*args)
        # this flag is going to be used in our game loop later, so it's global
        global skip_flag
        # let's prevent overlapping situations in our visualisation
        if output_coord in available_moves:
            skip_flag = False
            if curr_sign:
                cross(args[0].x // 100, args[0].y // 100)
            else:
                zero(args[0].x // 100, args[0].y // 100)
        else:
            skip_flag = True
    return wrapper


def interceptor(func):
    """ catches mouse click to transfer its coordinates on canvas to the global var"""
    def wrapper(*args):
        # just transfer the args to output
        global output_coord
        output_coord = (args[0].x // 100, args[0].y // 100)
        # print('intercepted')
        func(*args)
    return wrapper


@visualiser
@interceptor
def callback(click_event):
    # click_pos = (click_event.x // 100, click_event.y // 100)
    # print(click_pos)
    # unbinds mouse clicks after single use
    c.unbind('<Double-1>')
    # allows to use next button again
    passturn['text'] = 'Next'
    passturn['state'] = 'normal'
    passturn.focus_set()
    # allows using single clicks for the same purpose
    window.bind('<Button-3>', callback_extra)


def callback_extra(right_click_event):
    """right click anywhere as an alternative for the next button"""
    # we'll change next button's variable
    pass_var.set(1)


def waiter():
    """detects user clicks and waits till click + next button/right click are pressed"""
    # allow getting clicks and disable next button (same for single click) until we get double clicks
    c.bind('<Double-1>', callback)
    passturn['text'] = 'Click!'
    passturn['state'] = 'disabled'
    # temporarily focus to another object for better ux, let it be the canvas
    c.focus_set()

    window.unbind('<Button-3>')
    # stop until pass_var changes its value (0->1) <==> ensures that we don't proceed without clicking
    # print("waiting...")
    passturn.wait_variable(pass_var)
    # print("done waiting")
    # revert pass_var to default (0) for future use and disable right clicks and next button
    pass_var.set(0)
    passturn['text'] = 'Click!'
    passturn['state'] = 'disabled'
    window.unbind('<Button-3>')


def inverter(first_player):
    # let's also invert global sign flag for visualiser here
    global curr_sign
    curr_sign = not curr_sign
    # and return an inverted value to denote next player's turn
    return not first_player


def setup():
    """collects data from 2 config buttons and draws the playfield"""
    # playbtn['text'] = 'Restart!'
    playbtn['image'] = rl_img
    playfield()
    ch_cross = mode_var.get()
    real_2nd = p2type_var.get()
    return ch_cross, real_2nd


def counter(res_sign):
    """counts all wins for each sign and saves in global vars"""
    global count_O, count_X, max_score
    if res_sign:
        count_O += 1
    else:
        count_X += 1
    curr_max_score = max(count_X, count_O)
    max_score = update(curr_max_score)


def scoreboard(x_score, o_score):
    """updates scoreboard"""
    left_score['text'] = f"{x_score:02d}"
    right_score['text'] = f"{o_score:02d}"
    record_score['text'] = f"Record:{max_score:2d}"


def start_session():
    """initiates a new game after the play button has been pressed"""
    cfg = setup()
    g = Game(cfg)

    # set role alternation and while loop breaker parameters
    first_flag = True
    fin_flag = False

    # also update globals
    global curr_sign, available_moves
    # this flag is going to be used for visualization purposes
    curr_sign = cfg[0]
    # we have to make this a global variable too in order to use it in click interceptor
    available_moves = g.available_moves

    # main game cycle, returns either None or winner
    while not fin_flag:
        # let's check for any reason to end this game at each turn
        if not g.end:
            # determine if this is a first or real 2nd player's case
            if first_flag or g.p2.role:
                waiter()
                if not skip_flag:
                    g.step(first_flag, output_coord)
                else:
                    # debug purpose, just in case
                    print('Wrong move', output_coord)
            # we don't have to wait for clicks for our robot and there is no output_coord in this case
            else:
                # we will achieve this coordinate from g.step when output_coord=False
                robo = g.step(first_flag, False)
                if curr_sign:
                    cross(robo[0], robo[1])
                else:
                    zero(robo[0], robo[1])
            first_flag = inverter(first_flag)
            available_moves = g.available_moves
        else:
            if g.first_winner is None:
                winner = None
                print('DRAW!')
            elif g.first_winner is True:
                winner = g.p1
                print(f"First player {'X' if not curr_sign else 'O'} won!")
            else:
                winner = g.p2
                print(f"Second player {'X' if not curr_sign else 'O'} won!")
            # use winner's sign for a scoreboard
            if winner is not None:
                crossout(winner.moves)
                counter(curr_sign)
                scoreboard(count_X, count_O)
            # playbtn['text'] = 'Start!'
            playbtn['image'] = pl_img
            playbtn.focus_set()
            fin_flag = g.end


main_color = '#f0f3f5'
focus_color = '#fff0fb'
hl_color = '#a2d1f2'
canvas_color = '#fff0fb'

window = Tk()
window.title(" TTC game")
icon = Image.open("images/icon.png")
icon = icon.resize((35, 35), Image.Resampling.LANCZOS)
icon_tk = ImageTk.PhotoImage(icon)
window.iconphoto(False, icon_tk)
window.configure(background=main_color)
window.geometry("350x488")
window.minsize(350, 488)
window.maxsize(400, 550)



cr_img = Image.open("images/cross2.png")
cr_img = cr_img.resize((27, 27), Image.Resampling.LANCZOS)
cr_img = ImageTk.PhotoImage(cr_img)
zr_img = Image.open("images/zero.png")
zr_img = zr_img.resize((27, 27), Image.Resampling.LANCZOS)
zr_img = ImageTk.PhotoImage(zr_img)
pl_img = Image.open("images/play.png")
pl_img = pl_img.resize((27, 27), Image.Resampling.LANCZOS)
pl_img = ImageTk.PhotoImage(pl_img)
rl_img = Image.open("images/refresh.png")
rl_img = rl_img.resize((27, 27), Image.Resampling.LANCZOS)
rl_img = ImageTk.PhotoImage(rl_img)

lbl = Label(window, text="TicTacToe Game", font=("Oswald", 23), background=main_color)
lbl.grid(column=0, row=0, columnspan=5, pady=5)

middle_container = LabelFrame(window, relief=FLAT, background=main_color)
cfg_container = LabelFrame(middle_container, text="Config", labelanchor=NW, relief=GROOVE
                           , background=main_color, highlightcolor=hl_color)

# we have to set variable type first
mode_var = BooleanVar()
# setting default value
mode_var.set(1)
crossbtn = Radiobutton(cfg_container, variable=mode_var, value=1, image=cr_img, text='X', font=("Tahoma", 14, 'bold'),
                       indicatoron=0, background=main_color, selectcolor=focus_color, highlightcolor=hl_color)
# crossbtn.grid(column=0, row=1)
crossbtn.grid(column=0, row=0, padx=1, pady=3)
zerobtn = Radiobutton(cfg_container, variable=mode_var, value=0, image=zr_img, text='O', font=("Tahoma", 14, 'bold'),
                      indicatoron=0, background=main_color, selectcolor=focus_color, highlightcolor=hl_color)
# zerobtn.grid(column=0, row=2)
zerobtn.grid(column=1, row=0, padx=1, pady=3)
p2type_var = BooleanVar()
p2type_var.set(1)
p2type_btn = Checkbutton(cfg_container, variable=p2type_var, onvalue=0, offvalue=1, text='PC?', relief=GROOVE
                         , background=main_color, selectcolor=focus_color, highlightcolor=hl_color)
p2type_btn.grid(column=0, row=1, columnspan=2, padx=4, pady=5)

# initiate scoreboard with zeros by default
scoreboard_container = LabelFrame(middle_container, text="Scoreboard", labelanchor=N, relief=GROOVE
                                  , background=main_color, highlightcolor=hl_color)

left_score = Label(scoreboard_container, text=f"{count_X:02d}", font=("Tahoma", 20, 'bold'), padx=5
                   , background=main_color)
left_score.grid(column=0, row=0)
delimiter = Label(scoreboard_container, text="X vs O", justify=CENTER, font=("Tahoma", 15), background=main_color)
delimiter.grid(column=1, row=0)
right_score = Label(scoreboard_container, text=f"{count_O:02d}", font=("Tahoma", 20, 'bold'), padx=5
                    , background=main_color)
right_score.grid(column=2, row=0)
record_score = Label(scoreboard_container, text=f"Record:{update(0):2d}", font=("Tahoma", 15), background=main_color)
record_score.grid(column=0, row=1, columnspan=3, pady=3)

# join 2 control buttons into a single container for better positioning purpose
control_container = LabelFrame(middle_container, text="Action", labelanchor=NE, relief=GROOVE
                               , background=main_color, highlightcolor=hl_color)

playbtn = Button(control_container, image=pl_img, text=" Play! ", command=start_session, width=8,
                 relief=RIDGE, borderwidth=0.5, background=main_color, activebackground=focus_color,
                 highlightcolor=hl_color)
playbtn.focus_set()
playbtn.grid(column=0, row=0, pady=2, padx=3, sticky=N + S + W + E, ipady=3)
pass_var = BooleanVar()
pass_var.set(0)
passturn = Button(control_container, text="Next", command=lambda: pass_var.set(1), state='disabled', width=8,
                  relief=RIDGE, borderwidth=0.5, background=main_color, activebackground=focus_color,
                  highlightcolor=hl_color)
passturn.grid(column=0, row=1, pady=0, padx=3, sticky=N + S + W + E, ipady=3)

cfg_container.grid(column=0, row=0, rowspan=2, sticky=N + S + W + E, padx=2)
scoreboard_container.grid(column=1, row=0, rowspan=2, columnspan=3, sticky=N + S + W + E, padx=1)
control_container.grid(column=4, row=0, rowspan=2, sticky=N + S + W + E, padx=2)
middle_container.grid(column=0, row=1, columnspan=5, pady=2)

c = Canvas(window, bd=4, relief=GROOVE, height=300, width=300, bg=canvas_color, highlightthickness=0.5,
           highlightcolor=hl_color)
c.create_text(150, 150, text='Press play button to start\nClick twice to make a move,\nthen a right click to confirm.',
              justify=CENTER, font=("Helvetica", 15))
c.grid(column=0, row=3, columnspan=5, rowspan=5, padx=20, pady=5)


def playfield():
    """clears all canvas and creates new playfield"""
    c.delete("all")
    for t in range(0, 300, 100):
        c.create_line(t, -2, t, 304, width=3, fill="#574e55")
        c.create_line(-2, t, 304, t, width=3, fill="#574e55")


def zero(x, y):
    c.create_oval(20 + x * 100, 20 + y * 100, 81 + x * 100, 81 + y * 100, width=8)


def cross(x, y):
    c.create_text(50 + x * 100, 50 + y * 100, text="X", font=("Tahoma", 70))


def crossout(player_moves):
    """Looks simple at the very first glance but the problem is we don't know a winning pattern, so we have to figure
     it out from winner's moves list. Based on a last move, we restore a whole pattern. To cross it out
     in general, we must find 2 most distant points of 3 in this pattern. Ok, for 3x3 we could set up some conditions
     but let's try...a bit better approach. Then, we have to sort them to extend a line properly
     (to cross out a whole cells on sides)"""
    last_point = player_moves[-1]
    result3 = []
    for point in player_moves:
        test = line_approximation(point, last_point)
        if test in player_moves:
            result3 = [point, test]
            break
    result3.append(last_point)
    max_dist_points = distant_subset(result3)[0]
    addons = addon_calc(max_dist_points)
    endpoints = [(ep[0] * 100 + 50 + addons[ep][0] * 51, ep[1] * 100 + 50 + addons[ep][1] * 51) for ep in
                 max_dist_points]
    c.create_line(endpoints[0][0], endpoints[0][1], endpoints[1][0], endpoints[1][1], width=7, fill='red')


window.mainloop()


# just to test this opportunity, unused
def interceptor2(func):
    """this decorator intercepts click's coords if they're printed"""
    import io
    from contextlib import redirect_stdout

    def wrapper(*args):
        global output_coord
        # temporarily redirecting sys.stdout to string, new python feature
        with io.StringIO() as buffer, redirect_stdout(buffer):
            func(*args)
            output = buffer.getvalue()
        # dealing with output as a string of text to get click's coordinates
        output_coord = (int(output[1]), int(output[4]))
        print('intercepted')

    return wrapper

# original idea to visualise turns via eval to convert string to func name (cross/zero)
# eval(g.p1.fname)(turn1[0], turn1[1])
# eval(g.p2.fname)(turn2[0], turn2[1])
