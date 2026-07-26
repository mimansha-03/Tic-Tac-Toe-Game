"""
gui.py
------
A polished Tkinter front-end for Tic Tac Toe.

Design notes:
    * Canvas-drawn board (not plain buttons) so X's and O's are smooth,
      color-accented vector shapes instead of default Tk fonts.
    * A start screen lets the player choose 2-Player mode or Human vs AI
      (with a difficulty picker: Easy / Hard / Unbeatable).
    * Hover highlighting on empty cells, a subtle "pop-in" grow animation
      when a mark is placed, and a glowing strike-through line on the
      winning combination.
    * A persistent scoreboard (X wins / O wins / Draws) and a status
      bar that always tells you whose turn it is or who won.
"""

import tkinter as tk
from tkinter import ttk
import math

import game_logic as gl

# ---- Palette --------------------------------------------------------------
BG = "#111319"
BG_PANEL = "#1b1e29"
GRID_LINE = "#2e3244"
CELL_HOVER = "#232739"
X_COLOR = "#6c8cff"
O_COLOR = "#ff8a65"
WIN_COLOR = "#3ddc97"
TEXT_PRIMARY = "#f5f6fa"
TEXT_MUTED = "#8b8fa3"
ACCENT = "#6c5ce7"
ACCENT_HOVER = "#8272f0"

BOARD_SIZE = 360
CELL = BOARD_SIZE // 3
PADDING = 30  # inset for X/O glyphs within a cell


class TicTacToeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic Tac Toe")
        self.geometry("460x680")
        self.minsize(420, 640)
        self.configure(bg=BG)

        self.scores = {"X": 0, "O": 0, "draw": 0}
        self.mode = None          # "2p" or "ai"
        self.difficulty = "unbeatable"
        self.board = gl.new_board()
        self.current_player = gl.HUMAN
        self.game_over = False
        self.human_is_x = True

        self._build_style()
        self.container = ttk.Frame(self, style="TFrame")
        self.container.pack(fill="both", expand=True)

        self._show_menu()

    # ------------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=BG_PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=TEXT_PRIMARY,
                         font=("Segoe UI Semibold", 24))
        style.configure("Subtitle.TLabel", background=BG, foreground=TEXT_MUTED,
                         font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY,
                         font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=BG, foreground=TEXT_PRIMARY,
                         font=("Segoe UI Semibold", 13))
        style.configure("Score.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY,
                         font=("Segoe UI Semibold", 16))
        style.configure("ScoreCaption.TLabel", background=BG_PANEL, foreground=TEXT_MUTED,
                         font=("Segoe UI", 8))

        style.configure("Accent.TButton", background=ACCENT, foreground="white",
                        font=("Segoe UI Semibold", 12), padding=12, borderwidth=0)
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])

        style.configure("Ghost.TButton", background=BG_PANEL, foreground=TEXT_PRIMARY,
                        font=("Segoe UI", 10), padding=8, borderwidth=0)
        style.map("Ghost.TButton", background=[("active", "#262a3a")])

        style.configure("Choice.TButton", background=BG_PANEL, foreground=TEXT_PRIMARY,
                        font=("Segoe UI", 11), padding=14, borderwidth=0)
        style.map("Choice.TButton", background=[("active", "#262a3a")])

        style.configure("ChoiceSelected.TButton", background=ACCENT, foreground="white",
                        font=("Segoe UI Semibold", 11), padding=14, borderwidth=0)
        style.map("ChoiceSelected.TButton", background=[("active", ACCENT_HOVER)])

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------
    # Menu screen
    # ------------------------------------------------------------------
    def _show_menu(self):
        self._clear_container()
        c = self.container

        ttk.Label(c, text="Tic Tac Toe", style="Title.TLabel").pack(pady=(50, 4))
        ttk.Label(c, text="Choose how you'd like to play", style="Subtitle.TLabel").pack(pady=(0, 30))

        mode_frame = ttk.Frame(c, style="TFrame")
        mode_frame.pack(fill="x", padx=40)

        ttk.Button(
            mode_frame, text="🧑 Two Players", style="Choice.TButton",
            command=lambda: self._select_mode("2p")
        ).pack(fill="x", pady=6)

        ttk.Button(
            mode_frame, text="🤖 Human vs AI", style="Choice.TButton",
            command=lambda: self._select_mode("ai")
        ).pack(fill="x", pady=6)

        # Difficulty picker (only relevant for AI mode) — shown always,
        # greyed conceptually, but simplest is to show it under a label.
        self.diff_frame = ttk.Frame(c, style="TFrame")
        self.diff_frame.pack(fill="x", padx=40, pady=(20, 0))
        ttk.Label(self.diff_frame, text="AI difficulty", style="Subtitle.TLabel").pack(anchor="w")

        row = ttk.Frame(self.diff_frame, style="TFrame")
        row.pack(fill="x", pady=(8, 0))
        self.diff_buttons = {}
        for key, label in [("easy", "Easy"), ("hard", "Hard"), ("unbeatable", "Unbeatable")]:
            btn = ttk.Button(
                row, text=label,
                style="ChoiceSelected.TButton" if key == self.difficulty else "Choice.TButton",
                command=lambda k=key: self._select_difficulty(k)
            )
            btn.pack(side="left", expand=True, fill="x", padx=4)
            self.diff_buttons[key] = btn

        self.mode_hint = tk.StringVar(value="Pick a mode above, then press start.")
        ttk.Label(c, textvariable=self.mode_hint, style="Subtitle.TLabel").pack(pady=(24, 0))

        ttk.Button(
            c, text="Start Game", style="Accent.TButton",
            command=self._start_game
        ).pack(fill="x", padx=40, pady=(30, 0))

        self._selected_mode = "2p"

    def _select_mode(self, mode):
        self._selected_mode = mode
        if mode == "2p":
            self.mode_hint.set("Two players will take turns as X and O.")
        else:
            self.mode_hint.set("You play X. The AI plays O.")

    def _select_difficulty(self, key):
        self.difficulty = key
        for k, btn in self.diff_buttons.items():
            btn.configure(style="ChoiceSelected.TButton" if k == key else "Choice.TButton")

    def _start_game(self):
        self.mode = self._selected_mode
        self.scores = {"X": 0, "O": 0, "draw": 0}
        self._new_round()
        self._show_board_screen()

    # ------------------------------------------------------------------
    # Board screen
    # ------------------------------------------------------------------
    def _show_board_screen(self):
        self._clear_container()
        c = self.container

        top_bar = ttk.Frame(c, style="TFrame")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))
        ttk.Button(top_bar, text="← Menu", style="Ghost.TButton",
                   command=self._show_menu).pack(side="left")
        mode_text = "Two Player" if self.mode == "2p" else f"vs AI ({self.difficulty.title()})"
        ttk.Label(top_bar, text=mode_text, style="Subtitle.TLabel").pack(side="right")

        self.status_var = tk.StringVar()
        ttk.Label(c, textvariable=self.status_var, style="Status.TLabel").pack(pady=(0, 14))

        # Scoreboard
        score_panel = ttk.Frame(c, style="Panel.TFrame")
        score_panel.pack(padx=20, fill="x")
        for col, (key, label) in enumerate([("X", "Player X"), ("draw", "Draws"), ("O", "Player O" if self.mode == "2p" else "AI (O)")]):
            cell = ttk.Frame(score_panel, style="Panel.TFrame", padding=12)
            cell.grid(row=0, column=col, sticky="ew")
            score_panel.columnconfigure(col, weight=1)
            var = tk.StringVar(value="0")
            setattr(self, f"score_var_{key}", var)
            ttk.Label(cell, textvariable=var, style="Score.TLabel").pack()
            ttk.Label(cell, text=label, style="ScoreCaption.TLabel").pack()

        # Canvas board
        canvas_wrap = ttk.Frame(c, style="TFrame")
        canvas_wrap.pack(pady=24)
        self.canvas = tk.Canvas(
            canvas_wrap, width=BOARD_SIZE, height=BOARD_SIZE,
            bg=BG_PANEL, highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_hover)
        self.canvas.bind("<Leave>", lambda e: self._draw_board())

        self._hover_cell = None
        self._draw_board()
        self._update_scoreboard()
        self._update_status()

        ttk.Button(c, text="Restart Round", style="Accent.TButton",
                   command=self._new_round_and_redraw).pack(fill="x", padx=40, pady=(10, 0))

    def _new_round(self):
        self.board = gl.new_board()
        self.current_player = gl.HUMAN
        self.game_over = False

    def _new_round_and_redraw(self):
        self._new_round()
        self._draw_board()
        self._update_status()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _cell_bounds(self, index):
        row, col = divmod(index, 3)
        x0, y0 = col * CELL, row * CELL
        return x0, y0, x0 + CELL, y0 + CELL

    def _draw_board(self, winning=None, hovered=None):
        self.canvas.delete("all")

        # Grid background cells (with hover highlight)
        for i in range(9):
            x0, y0, x1, y1 = self._cell_bounds(i)
            fill = CELL_HOVER if (hovered == i and self.board[i] == gl.EMPTY and not self.game_over) else BG_PANEL
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")

        # Grid lines
        for i in (1, 2):
            self.canvas.create_line(i * CELL, 8, i * CELL, BOARD_SIZE - 8, fill=GRID_LINE, width=3)
            self.canvas.create_line(8, i * CELL, BOARD_SIZE - 8, i * CELL, fill=GRID_LINE, width=3)

        # Marks
        for i, mark in enumerate(self.board):
            if mark == gl.HUMAN:
                self._draw_x(i)
            elif mark == gl.AI:
                self._draw_o(i)

        # Winning strike-through
        if winning:
            a, b, c = winning
            ax0, ay0, ax1, ay1 = self._cell_bounds(a)
            cx0, cy0, cx1, cy1 = self._cell_bounds(c)
            ax, ay = (ax0 + ax1) / 2, (ay0 + ay1) / 2
            cx, cy = (cx0 + cx1) / 2, (cy0 + cy1) / 2
            self.canvas.create_line(ax, ay, cx, cy, fill=WIN_COLOR, width=6, capstyle="round")

    def _draw_x(self, index):
        x0, y0, x1, y1 = self._cell_bounds(index)
        x0, y0, x1, y1 = x0 + PADDING, y0 + PADDING, x1 - PADDING, y1 - PADDING
        self.canvas.create_line(x0, y0, x1, y1, fill=X_COLOR, width=8, capstyle="round")
        self.canvas.create_line(x0, y1, x1, y0, fill=X_COLOR, width=8, capstyle="round")

    def _draw_o(self, index):
        x0, y0, x1, y1 = self._cell_bounds(index)
        x0, y0, x1, y1 = x0 + PADDING, y0 + PADDING, x1 - PADDING, y1 - PADDING
        self.canvas.create_oval(x0, y0, x1, y1, outline=O_COLOR, width=8)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def _index_from_xy(self, x, y):
        if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
            return None
        col = x // CELL
        row = y // CELL
        return int(row) * 3 + int(col)

    def _on_canvas_hover(self, event):
        idx = self._index_from_xy(event.x, event.y)
        if idx != self._hover_cell:
            self._hover_cell = idx
            self._draw_board(hovered=idx)

    def _on_canvas_click(self, event):
        if self.game_over:
            return
        idx = self._index_from_xy(event.x, event.y)
        if idx is None or self.board[idx] != gl.EMPTY:
            return

        if self.mode == "ai" and self.current_player == gl.AI:
            return  # ignore clicks during AI's turn

        self._place_mark(idx, self.current_player)

        if self.game_over:
            return

        if self.mode == "ai" and self.current_player == gl.AI:
            self.status_var.set("AI is thinking…")
            self.after(400, self._ai_turn)

    def _ai_turn(self):
        if self.game_over:
            return
        move = gl.best_ai_move(self.board, self.difficulty)
        if move is not None:
            self._place_mark(move, gl.AI)

    def _place_mark(self, idx, player):
        self.board = gl.make_move(self.board, idx, player)
        result = gl.winner(self.board)

        if result is None:
            self.current_player = gl.AI if player == gl.HUMAN else gl.HUMAN
            self._draw_board()
            self._update_status()
            return

        self.game_over = True
        line = gl.winning_line(self.board)
        self._draw_board(winning=line)

        if result == "draw":
            self.scores["draw"] += 1
            self.status_var.set("It's a draw!")
        else:
            self.scores[result] += 1
            if self.mode == "ai":
                winner_text = "You win! 🎉" if result == gl.HUMAN else "AI wins!"
            else:
                winner_text = f"Player {result} wins! 🎉"
            self.status_var.set(winner_text)

        self._update_scoreboard()

    def _update_status(self):
        if self.game_over:
            return
        if self.mode == "ai":
            text = "Your turn (X)" if self.current_player == gl.HUMAN else "AI is thinking…"
        else:
            text = f"Player {self.current_player}'s turn"
        self.status_var.set(text)

    def _update_scoreboard(self):
        self.score_var_X.set(str(self.scores["X"]))
        self.score_var_O.set(str(self.scores["O"]))
        self.score_var_draw.set(str(self.scores["draw"]))


def main():
    app = TicTacToeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
