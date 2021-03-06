import itertools
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import BOTH, CENTER, RIGHT, LEFT, RAISED, Text
from tkinter.ttk import Frame, Button, Style
from src.conf.settings import messages
from src.board import Board

phases = {
    'P': 'Choose Piece',
    'T': 'Choose Target'
}
turns = {
    'W': 'White plays',
    'B': 'Black plays'
}


class GameExecution(tk.Frame):

    def __init__(self, mode, board):
        super().__init__()

        self.phase_iter = itertools.cycle('PT')
        self.turn_iter = itertools.cycle('WB')

        self.mode = mode
        self.board = board
        self.turn = next(self.turn_iter)
        self.phase = next(self.phase_iter)
        self.go_on = True

        self.config(background='black')
        self.style = Style()

        self.init_ui()
        values = {}
        self.values = {}
        for v1 in 'phbqkt':
            for v2 in 'bw':
                for v3 in 'bw':
                    values[v1 + v2 + v3] = eval("Image.open('src/images/" + v1 + v2 + v3 + ".jpg')")
                    self.values[v1 + v2 + v3] = ImageTk.PhotoImage(values[v1 + v2 + v3])
                    self.label = tk.Label(image=self.values[v1 + v2 + v3])
                    self.label.values = dict()
                    self.label.values[v1 + v2 + v3] = self.values[v1 + v2 + v3]

        self.piece_to_move = ''
        self.place_to_move = ''

    def init_ui(self):
        """
        This method initializes the GUI.
        """
        self.master.title("Python Chess")
        self.pack(fill=BOTH, expand=1)
        self.center_window()
        self.message_board()
        self.restart_button()
        self.close_button()

    def center_window(self):
        """
        This method prepares the board interface.
        """
        w = 625
        h = 664

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()

        x = (sw - w)/2
        y = (sh - h)/2

        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.style.theme_use("default")

        my_text = Text(self, width=100, height=41)
        my_text.config(background='LightSteelBlue')
        my_text.insert('2.2', ' '*7 + (' '*10).join('123') + ' '*9 + (' '*9).join('45') + ' '*10 + (' '*10).join('67') + ' '*9 + '8')
        my_text.insert('2.2', '\n\n\n A' + '\n'*5 + ' B' + '\n'*5 + ' C' + '\n'*5 + ' D' + '\n'*5 + ' E' + '\n'*5 + ' F' + '\n'*5 + ' G' + '\n'*5 + ' H')
        my_text.pack()

    def message_board(self):
        """
        This method prepares the message interface.
        """
        self.frame = Frame(self, relief=RAISED, borderwidth=1)
        self.frame.pack(fill=BOTH, expand=True)

        self.my_text = Text(self, width=63, height=2)
        self.my_text.insert('1.0',
                            turns[self.turn] + ' - ' + phases[self.phase])
        self.my_text.pack(side=LEFT, padx=5)

    def restart_button(self):
        """
        This method prepares the restart button.
        :return:
        """
        button_style = Style()
        button_style.configure("TButton", background='white')
        close_button = Button(self,
                              text="Restart",
                              command=lambda: self.restart())
        close_button.pack(side=LEFT, padx=5, pady=5)

    def close_button(self):
        """
        This method prepares the close button.
        :return:
        """
        button_style = Style()
        button_style.configure("TButton", background='white')
        close_button = Button(self,
                              text="Quit",
                              command=self.quit)
        close_button.pack(side=RIGHT, padx=5, pady=5)

    def restart(self):
        board = Board(8, 8)
        self.board = board
        self.phase_iter = itertools.cycle('PT')
        self.turn_iter = itertools.cycle('WB')
        self.turn = next(self.turn_iter)
        self.phase = next(self.phase_iter)
        self.go_on = True
        self.piece_to_move = ''
        self.place_to_move = ''
        self.my_text.insert('1.0',
                            turns[self.turn] + ' - ' + phases[self.phase] + ' |White:' + self.board.white_timer.format_time() + ' Black:' + self.board.black_timer.format_time() + '\n\n')
        self.my_text.pack(side=LEFT, padx=5)
        self.show_board()

    def pressed(self, position):
        """
        This method is called every time a board button is pressed. It
        checks the current turn and phase, to check if the pressed button
        belongs to a possible situation, and acts consequently.
        :param position: (tuple) the position of the pressed button.
        """
        if self.go_on:
            pos_value = self.board.get_pos_val(position)
            if self.phase == 'P' and pos_value[1] == self.turn:
                self.piece_to_move = position
                self.phase = next(self.phase_iter)
                if self.mode == 'learn':
                    self.board.check_movements(position)
            elif self.phase == 'T':
                self.place_to_move = position
                corr_mov = self.board.check_correct_move(self.piece_to_move,
                                                         self.place_to_move)
                if corr_mov['output']:
                    self.go_on = self.board.move_piece(self.piece_to_move,
                                                       self.place_to_move)
                    self.turn = next(self.turn_iter)
                else:
                    self.my_text.insert('1.0', corr_mov['errors'] + '\n')
                self.phase = next(self.phase_iter)
            if self.go_on:
                if self.phase == "T":
                    space = '|'
                else:
                    space = ' |'
                self.my_text.insert('1.0',
                                    turns[self.turn] + ' - ' + phases[self.phase] + space + 'White:' + self.board.white_timer.format_time() + ' Black:' + self.board.black_timer.format_time() + '\n')
            else:
                self.my_text.insert('1.0',
                                    messages['PLAYER_WIN'].format(self.board.obtain_other_turn(self.turn).upper()) + '\n')
            self.my_text.pack(side=LEFT, padx=5)
            # self.board.print_board_in_terminal()
        self.show_board()

    def show_board(self):
        """
        This method creates all the buttons needed to represent a board in
        the current game instance.
        """
        button_style = Style()
        button_style.configure("B.TLabel", background='black')
        button_style.configure("W.TLabel", background='white')
        button_style.configure("Y.TLabel", background='yellow')
        button_style.configure("R.TLabel", background='red')
        button_style.configure("G.TLabel", background='green')
        param = ''
        for in1, x in enumerate(self.board.squares):
            for in2, y in enumerate(x):
                if (in1 + in2) % 2 == 1:
                    color = 'B'
                    try:
                        param = eval('self.values["' + y.lower()[0:2] + 'b"]')
                    except KeyError:
                        pass
                else:
                    color = 'W'
                    try:
                        param = eval('self.values["' + y.lower()[0:2] + 'w"]')
                    except KeyError:
                        pass
                if y[2] == 'k' or y[3] == 'c' or y[4] == 'l':
                    if y[2] == 'k':
                        color = 'R'
                    elif y[3] == 'c':
                        color = 'Y'
                    elif y[4] == 'l':
                        color = 'G'
                    self.board.put_pos_val((in1, in2),
                                           self.board.get_pos_val(
                                               (in1, in2))[0:2] + '   ')
                if y.lower()[0:4] != '    ':
                    but = Button(self,
                                 style=color+".TLabel",
                                 command=lambda v=(in1, in2): self.pressed(v),
                                 image=param,
                                 compound=CENTER)
                else:
                    but = Button(self,
                                 style=color+".TLabel",
                                 command=lambda v=(in1, in2): self.pressed(v))

                but.place(x=(74*in2) + 25, y=(74*in1)+25, width=68, height=68)
        self.pack()
