import numpy as np
import copy
import tkinter as tk
from tkinter import messagebox
import threading
from typing import List, Optional
import tkinter.font as tkFont

# Create initial board with numbers 1 to 9
def make_board():
    return np.array([[str(i * 3 + j + 1) for j in range(3)] for i in range(3)])

def print_board(board):
    for i in range(3):
        print(" " + "  |  ".join(str(board[i][j]) for j in range(3)))
        if i != 2:
            print("----|-----|----")

def next_player(cp):
    return 'O' if cp == 'X' else 'X'

def actions(board):
    return [str(board[i][j]) for i in range(3) for j in range(3) if board[i][j] not in ['X', 'O']]

def result(board, action, player):
    new_board = copy.deepcopy(board)
    found = False
    for i in range(3):
        for j in range(3):
            if new_board[i][j] == action:
                new_board[i][j] = player
                found = True
                break
        if found:
            break
    if not found:
        raise ValueError("Invalid action: Cell not found")
    return new_board

def check_winner(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] in ['X', 'O']:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] in ['X', 'O']:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] in ['X', 'O']:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] in ['X', 'O']:
        return board[0][2]
    for i in range(3):
        for j in range(3):
            if board[i][j] not in ['X', 'O']:
                return None
    return 'Draw'

def terminal(res):
    return res in ['X', 'O', 'Draw']

def utility(res):
    if res == 'X':
        return 1
    if res == 'O':
        return -1
    if res == 'Draw':
        return 0

def minmax(board, player, alpha=-float('inf'), beta=float('inf')):
    winner = check_winner(board)
    if terminal(winner):
        return (None, utility(winner))

    if player == 'X':  # Maximizer
        best_score = -float('inf')
        best_move = None
        for action in actions(board):
            new_board = result(board, action, player)
            _, score = minmax(new_board, next_player(player), alpha, beta)

            if score > best_score:
                best_score = score
                best_move = action

            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # Prune remaining branches

        return best_move, best_score

    else:  # Minimizer
        best_score = float('inf')
        best_move = None
        for action in actions(board):
            new_board = result(board, action, player)
            _, score = minmax(new_board, next_player(player), alpha, beta)

            if score < best_score:
                best_score = score
                best_move = action

            beta = min(beta, best_score)
            if beta <= alpha:
                break  # Prune remaining branches

        return best_move, best_score

# ------------------------ GUI Implementation ------------------------

# --- Modern color theme ---
BG_COLOR = '#22223b'
GRID_COLOR = '#4a4e69'
X_COLOR = '#f2e9e4'
O_COLOR = '#9a8c98'
HOVER_COLOR = '#c9ada7'
FONT = ("Segoe UI", 36, "bold")
SMALL_FONT = ("Segoe UI", 16)

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - The Best GUI Ever!")
        self.root.geometry("420x560")
        self.root.resizable(False, False)
        # Gradient background
        self.bg_canvas = tk.Canvas(self.root, width=420, height=560, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.draw_gradient()
        # Custom fonts
        self.title_font = tkFont.Font(family="Segoe Script", size=32, weight="bold")
        self.score_font = tkFont.Font(family="Segoe UI", size=16, weight="bold")
        self.button_font = tkFont.Font(family="Segoe UI", size=36, weight="bold")
        self.board = make_board()
        self.current_player = 'X'  # AI starts
        self.buttons: List[List[tk.Button]] = []
        self.create_widgets()
        self.locked = False
        self.score = {'X': 0, 'O': 0, 'Draw': 0}
        self.update_scoreboard()
        self.root.after(500, self.ai_move_if_needed)
        self.winning_cells = []

    def draw_gradient(self):
        # Vertical gradient from #22223b to #4a4e69
        for i in range(560):
            r1, g1, b1 = 34, 34, 59
            r2, g2, b2 = 74, 78, 105
            r = int(r1 + (r2 - r1) * i / 560)
            g = int(g1 + (g2 - g1) * i / 560)
            b = int(b1 + (b2 - b1) * i / 560)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.bg_canvas.create_line(0, i, 420, i, fill=color)

    def create_widgets(self):
        # Title Banner
        self.title_label = tk.Label(self.root, text="Tic Tac Toe", font=self.title_font, bg='#4a4e69', fg='#f2e9e4', pady=10, bd=0)
        self.title_label.place(x=0, y=10, width=420, height=60)
        # Scoreboard
        self.score_label = tk.Label(self.root, text='', font=self.score_font, bg='#22223b', fg='#c9ada7')
        self.score_label.place(x=0, y=75, width=420, height=30)
        # Board
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(self.root, text='', font=self.button_font, width=4, height=2,
                                bg='#22223b', fg='#f2e9e4', bd=0, relief='flat',
                                activebackground='#9a8c98', activeforeground='#f2e9e4',
                                command=lambda r=i, c=j: self.on_click(r, c),
                                highlightthickness=0)
                btn.place(x=40 + j*110, y=120 + i*110, width=100, height=100)
                btn.bind('<Enter>', lambda e, r=i, c=j: self.on_hover(r, c, True))
                btn.bind('<Leave>', lambda e, r=i, c=j: self.on_hover(r, c, False))
                # Rounded corners and shadow effect
                btn.after(0, lambda b=btn: b.config(highlightbackground='#c9ada7', highlightcolor='#c9ada7'))
                row.append(btn)
            self.buttons.append(row)
        # Animated Play Again button
        self.reset_btn = tk.Button(self.root, text='Play Again', font=self.score_font, bg='#9a8c98', fg='#22223b',
                                   command=self.reset, relief='flat', bd=0, activebackground='#f2e9e4', activeforeground='#22223b')
        self.reset_btn.place(x=110, y=470, width=200, height=50)
        self.reset_btn.bind('<Enter>', lambda e: self.reset_btn.config(bg='#f2e9e4', fg='#4a4e69'))
        self.reset_btn.bind('<Leave>', lambda e: self.reset_btn.config(bg='#9a8c98', fg='#22223b'))

    def update_scoreboard(self):
        self.score_label.config(text=f"Score - AI (X): {self.score['X']}  You (O): {self.score['O']}  Draws: {self.score['Draw']}")

    def on_hover(self, r, c, enter):
        btn = self.buttons[r][c]
        if btn['text'] == '' and not self.locked:
            btn['bg'] = '#c9ada7' if enter else '#22223b'
            btn['fg'] = '#22223b' if enter else '#f2e9e4'

    def on_click(self, r, c):
        if self.locked or self.board[r][c] in ['X', 'O']:
            return
        self.make_move(r, c, 'O')
        self.after_move()

    def make_move(self, r, c, player):
        self.board[r][c] = player
        self.buttons[r][c]['text'] = player
        self.buttons[r][c]['fg'] = '#f2e9e4' if player == 'X' else '#9a8c98'
        self.buttons[r][c]['bg'] = '#22223b'
        self.buttons[r][c]['activebackground'] = '#9a8c98'
        self.buttons[r][c]['font'] = self.button_font
        self.buttons[r][c].update()

    def after_move(self):
        winner = check_winner(self.board)
        if terminal(winner):
            self.locked = True
            self.highlight_winner(winner)
            self.show_endgame(winner)
            return
        if self.current_player == 'O':
            self.current_player = 'X'
            self.root.after(400, self.ai_move_if_needed)
        else:
            self.current_player = 'O'

    def ai_move_if_needed(self):
        if self.current_player == 'X' and not self.locked:
            def ai_move():
                move, _ = minmax(self.board, 'X')
                if move:
                    for i in range(3):
                        for j in range(3):
                            if self.board[i][j] == move:
                                self.root.after(0, lambda i=i, j=j: (self.make_move(i, j, 'X'), self.after_move()))
                                return
            threading.Thread(target=ai_move).start()

    def highlight_winner(self, winner):
        self.winning_cells = self.get_winning_cells(winner)
        if self.winning_cells:
            for (i, j) in self.winning_cells:
                self.buttons[i][j].config(bg='#f2e9e4', fg='#22223b')
                self.buttons[i][j].update()

    def get_winning_cells(self, winner):
        if winner not in ['X', 'O']:
            return []
        # Rows
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == winner:
                return [(i, 0), (i, 1), (i, 2)]
        # Columns
        for j in range(3):
            if self.board[0][j] == self.board[1][j] == self.board[2][j] == winner:
                return [(0, j), (1, j), (2, j)]
        # Diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == winner:
            return [(0, 0), (1, 1), (2, 2)]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == winner:
            return [(0, 2), (1, 1), (2, 0)]
        return []

    def show_endgame(self, winner):
        msg = ''
        if winner == 'Draw':
            msg = "It's a draw!"
            self.score['Draw'] += 1
        elif winner == 'X':
            msg = "AI (X) wins!"
            self.score['X'] += 1
        else:
            msg = "You (O) win!"
            self.score['O'] += 1
        self.update_scoreboard()
        self.root.after(700, lambda: messagebox.showinfo("Game Over", msg))

    def reset(self):
        self.board = make_board()
        self.locked = False
        self.current_player = 'X'
        self.winning_cells = []
        for i in range(3):
            for j in range(3):
                btn = self.buttons[i][j]
                btn['text'] = ''
                btn['bg'] = '#22223b'
                btn['fg'] = '#f2e9e4'
                btn['activebackground'] = '#9a8c98'
                btn['font'] = self.button_font
        self.root.after(400, self.ai_move_if_needed)

# --- Run the GUI ---
if __name__ == "__main__":
    # Comment out the CLI game loop
    # board = make_board()
    # current_player = 'X'  # AI starts
    # print("Welcome to Tic Tac Toe!")
    # print("You are O. AI is X.\n")
    # while True:
    #     print_board(board)
    #     result_now = check_winner(board)
    #     if terminal(result_now):
    #         if result_now == 'Draw':
    #             print("It's a draw!")
    #         else:
    #             print(f"Player {result_now} wins!")
    #         break
    #     if current_player == 'X':
    #         print("\nAI is thinking...")
    #         move, _ = minmax(board, 'X')
    #         board = result(board, move, 'X')
    #     else:
    #         print("\nYour turn.")
    #         print("Available moves:", actions(board))
    #         move = input("Enter your move: ")
    #         while move not in actions(board):
    #             print("Invalid move. Try again.")
    #             move = input("Enter your move: ")
    #         board = result(board, move, 'O')
    #     current_player = next_player(current_player)
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()

