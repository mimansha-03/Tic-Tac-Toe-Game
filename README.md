# ⭕ Tic Tac Toe (Python + Tkinter)

A polished desktop Tic Tac Toe game with a dark, modern UI, a canvas-drawn
board, an unbeatable Minimax AI, and a classic 2-player mode.

## Features

- 🎨 **Custom canvas-drawn board** — smooth vector X's and O's with
  color accents, not default Tk text/buttons.
- 🖱️ **Hover highlighting** on empty cells and a glowing strike-through
  line drawn across the winning combination.
- 🤖 **Human vs AI mode** with 3 difficulty levels:
  - **Easy** — fully random moves.
  - **Hard** — mostly optimal, occasionally makes a mistake.
  - **Unbeatable** — perfect Minimax play; it will never lose.
- 🧑‍🤝‍🧑 **2-Player mode** — play locally, taking turns as X and O.
- 🧮 **Scoreboard** that tracks X wins / O wins / Draws across rounds.
- 🧵 AI "thinking" has a short, deliberate delay so it doesn't feel
  instantaneous/robotic.
- ✅ **Unit tested** game logic and AI (decoupled from the UI).

## Project structure

```
tic_tac_toe/
├── main.py             # Entry point — run this
├── gui.py               # Tkinter UI (menu screen + canvas board)
├── game_logic.py          # Board state, win detection, Minimax AI (no UI dependency)
├── test_game_logic.py       # Unit tests for game_logic.py
├── requirements.txt        # Dependency notes (stdlib only)
└── README.md            # This file
```

## Requirements

- Python 3.8+
- Tkinter (bundled with most Python installs — see `requirements.txt`
  if it's missing on Linux)

## Setup & Run

```bash
# 1. Unzip the project and move into it
cd tic_tac_toe

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Run it — no pip installs needed!
python main.py
```

## Running the tests

```bash
python -m unittest test_game_logic.py -v
```

## How the AI works

The AI uses the **Minimax algorithm** — it recursively explores every
possible sequence of remaining moves, scoring a finished game as +10
for an AI win, -10 for a human win, and 0 for a draw (each adjusted
slightly by search depth so the AI prefers *faster* wins and *slower*
losses). It then picks the move that guarantees the best worst-case
outcome. On "Unbeatable", this means the AI can, at absolute worst,
force a draw — it can never actually lose.

- **Easy** picks a uniformly random legal move.
- **Hard** uses Minimax 80% of the time and a random move the other
  20%, so it plays strongly but is beatable.

## Customizing

- **Colors/theme**: all colors are defined as constants at the top of
  `gui.py` (`X_COLOR`, `O_COLOR`, `WIN_COLOR`, etc.).
- **Board size**: change `BOARD_SIZE` in `gui.py`.
- **AI "thinking" delay**: change the `self.after(400, ...)` call in
  `gui.py`'s `_on_canvas_click`.

## License

Free to use, modify, and distribute for personal or commercial projects.
