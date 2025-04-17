""" Quantum Xs and Os Game """

import cirq
import tkinter as tk

# Set the main window:
main_wind = tk.Tk()
main_wind.title("Quantum Xs and Os game")
WIDTH = 1280 # The main window width in pixels
HEIGHT = 800 # The main window height in pixels
main_wind.geometry(f"{WIDTH}x{HEIGHT}")


# Set the game info table:
fr1 = tk.Frame(master=main_wind, borderwidth=3, relief=tk.SUNKEN)
fr1.pack(side=tk.TOP)

info = tk.Label(master=fr1, text="Choose quantum uncertainty in X and O")
info.pack(fill="x")

# Set the game start and reset buttons:
fr2 = tk.Frame(master=main_wind, borderwidth=3, relief=tk.RAISED)
fr2.place(relx=0.3, rely=0.1)

strb = tk.Button(master=fr2, text="Start")
strb.pack(side="left", ipadx=10)

rstb = tk.Button(master=fr2, text="Reset")
rstb.pack(side="right", ipadx=10)

# Set the game board:
fr3 = tk.Frame(master=main_wind, borderwidth=3, relief=tk.RAISED)
fr3.place(relx=0.14, rely=0.25)

_SIZE = 3 # Size of the game board
cells = {} # Make dictionary of cells
for row in range(_SIZE):
    for col in range(_SIZE):
        btn = tk.Button(master=fr3)
        btn.grid(row=row, column=col)
        cells[btn] = (row, col)


# Set the control panel:
fr4 = tk.Frame(master=main_wind, borderwidth=1, relief=tk.SUNKEN)
fr4.place(relx=0.43, rely=0.21)

lg = WIDTH*0.47

scl1 = tk.Scale(master=fr4, label="Quantum uncertainty in X",
orient= "horizontal", from_=0, to=1, length=lg, tickinterval=0.1,
resolution=0.1, showvalue="no")
scl1.grid(row=0, column=0)

scl2 = tk.Scale(master=fr4, label="Quantum uncertainty in O",
orient= "horizontal", from_=0, to=1, length=lg, tickinterval=0.1,
resolution=0.1, showvalue="no")
scl2.grid(row=1, column=0)


# Set the instruction:
fr5 = tk.Frame(master=main_wind, borderwidth=1, relief=tk.GROOVE)
fr5.place(relx=0.3, rely=0.7)

wd = WIDTH*0.7

inst = tk.Message(master=fr5,
text="GAME INSTRUCTION\n\n1. Choose quantum uncertainty by clicking and\
 sliding the button:\n    0 corresponds to classical game, 1 corresponds\
 to X-O swap,\n    intermediate values define quantum probability of getting\
  X and O.\n2. Click 'Start' button and begin the game.\n\
3. To play again click 'Reset' button.", width=wd)
inst.pack(fill=tk.X, expand=tk.YES)


# Read off the control parameters:
prms = {} # Dictionary of quantum uncertainty parameters
moves = [] # Moves record

def get_value1(event):
    qX = scl1.get()
    info["text"] = f"Quantum uncertainty in X = {qX}"
    prms["qX"] = qX

def get_value2(event):
    qO = scl2.get()
    info["text"] = f"Quantum uncertainty in O = {qO}"
    prms["qO"] = qO

scl1.bind("<ButtonRelease-1>", get_value1)
scl2.bind("<ButtonRelease-1>", get_value2)

def start(event):
    if 'qX' in prms and 'qO' in prms:
        info["text"] = "X's move"

def restart(event):
    moves.clear()
    prms.clear()
    scl1.set(0)
    scl2.set(0)
    info["text"] = "Choose quantum uncertainty in X and O"
    for btn in cells.keys():
        btn["text"] = ""

strb.bind("<ButtonPress-1>", start)
rstb.bind("<ButtonPress-1>", restart)

# Game:

# Quantum cells:
def bitstr(bits):
    for b in bits:
        if b:
            return "X"
        else:
            return "O"

def qcell(name,pow):
    qubit = cirq.NamedQubit(name)
    circ = cirq.Circuit()
    circ.append(cirq.X(qubit)**pow)
    circ.append(cirq.measure(qubit))
    simulator = cirq.Simulator()
    result = simulator.run(circ)
    return bitstr(result.measurements.values())

def move(event):
    if info["text"] == "X's move" and event.widget["text"] == "":
        symb = qcell("X",1+prms["qX"])
        event.widget["text"] = symb
        moves.append(symb)
        if win():
            info["text"] = event.widget["text"] + " won the game!"
            print(f"moves = {moves}")
        else:
            info["text"] = "O's move"
    elif info["text"] == "O's move" and event.widget["text"] == "":
        symb = qcell("O",prms["qO"])
        event.widget["text"] = symb
        moves.append(symb)
        if win():
            info["text"] = event.widget["text"] + " won the game!"
            print(f"moves = {moves}")
        else:
            info["text"] = "X's move"
    if len(moves) == _SIZE*_SIZE and not win():
        info["text"] = "Draw!"
        print(f"moves = {moves}")

def win():
    """ Find winning combinations among n rows, n columns, and 2 diagonals
    and highlight the cells in red. """
    btns = list(cells.keys()) # All game field buttons
    w = False
    for i in range(_SIZE):
        for j in range(0+_SIZE*i,_SIZE-1+_SIZE*i):
            if not (btns[j]["text"] == btns[j+1]["text"] != ""):
                break
        else:
            w = True
    for i in range(_SIZE):
        for j in range(0+i,_SIZE*(_SIZE-1)+i,_SIZE):
            if not (btns[j]["text"] == btns[j+_SIZE]["text"] != ""):
                break
        else:
            w = True
    for i in range(0,_SIZE*_SIZE-1,_SIZE+1):
        if not (btns[i]["text"] == btns[i+_SIZE+1]["text"] != ""):
            break
    else:
        w = True
    for i in range(_SIZE-1,_SIZE*(_SIZE-1),_SIZE-1):
        if not (btns[i]["text"] == btns[i+_SIZE-1]["text"] != ""):
            break
    else:
        w = True
    return w


for btn in cells.keys():
    btn.bind("<ButtonPress-1>", move)


# Run the interface:
main_wind.mainloop()