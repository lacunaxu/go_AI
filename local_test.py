# local_test.py - Local Testing Script for my_player3 vs random_player
import os
import subprocess
import shutil
import time
from read import readInput
from host import GO

# Set paths
MY_AGENT = "my_player.py"
RANDOM_AGENT = "random_player.py"
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"

# Initialize empty board
def init_board():
    with open(INPUT_FILE, 'w') as f:
        f.write("1\n")  # Black starts
        for _ in range(5):
            f.write("00000\n")  # Previous board
        for _ in range(5):
            f.write("00000\n")  # Current board

# Run one move of agent
def run_agent(agent_path):
    subprocess.run(["python3", agent_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Load board state
def load_board():
    piece_type, prev_board, curr_board = readInput(5)
    return piece_type, prev_board, curr_board

# Display board in console
def print_board(board):
    symbols = {0: '.', 1: 'X', 2: 'O'}
    print("\nBoard:")
    for row in board:
        print(" ".join(symbols[cell] for cell in row))
    print()

# Simulate one game
def simulate_game():
    init_board()
    game_over = False
    moves = 0
    current_agent = RANDOM_AGENT  # Random goes first (Black)

    while not game_over:
        run_agent(current_agent)

        # Validate move
        piece_type, prev_board, curr_board = load_board()
        go = GO(5)
        go.set_board(piece_type, prev_board, curr_board)

        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

        go.visualize_board()

        winner = go.judge_winner() if go.game_end(piece_type, action="MOVE") else None

        if winner is not None:
            print(f"\nGame Over! Winner: {'Random' if winner == 1 else 'MCTS' if winner == 2 else 'Tie'}")
            game_over = True
            return winner

        moves += 1
        current_agent = MY_AGENT if current_agent == RANDOM_AGENT else RANDOM_AGENT

if __name__ == "__main__":
    total_games = 2
    mcts_wins = 0
    random_wins = 0
    ties = 0

    for i in range(total_games):
        print(f"\n===== Game {i+1} =====")
        result = simulate_game()
        if result == 1:
            random_wins += 1
        elif result == 2:
            mcts_wins += 1
        else:
            ties += 1

    print("\n===== Summary =====")
    print(f"MCTS Wins: {mcts_wins}, Random Wins: {random_wins}, Ties: {ties}")
