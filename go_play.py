import argparse
import subprocess
import os
import sys
import time
from read import readInput
from write import writeNextInput
from host import GO

def print_board(board):
    symbols = {0: '.', 1: 'X', 2: 'O'}
    for row in board:
        print(" ".join(symbols[cell] for cell in row))
    print()

def call_player(player_script):
    # 执行AI或玩家脚本
    if player_script == "manual":
        move = input("Your move (row,col) or PASS: ")
        with open("output.txt", "w") as f:
            if move.strip().upper() == "PASS":
                f.write("PASS")
            else:
                f.write(move.strip())
    else:
        subprocess.run(["python", f"{player_script}.py"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=5, help="board size")
    parser.add_argument("-p1", type=str, default="my_player", help="player 1 script (no .py)")
    parser.add_argument("-p2", type=str, default="random_player", help="player 2 script")
    parser.add_argument("-t", type=int, default=1, help="print board")
    args = parser.parse_args()

    size = args.n
    p1 = args.p1
    p2 = args.p2
    verbose = args.t == 1

    # 初始化空棋盘
    empty_board = [[0] * size for _ in range(size)]
    writeNextInput(1, empty_board, empty_board)

    piece_type = 1
    moves = 0
    consecutive_passes = 0

    while True:
        if verbose:
            print(f"=== Turn {moves+1} | Player {piece_type} ({'X' if piece_type==1 else 'O'}) ===")

        # 调用玩家
        current_player = p1 if piece_type == 1 else p2
        call_player(current_player)

        # 读取输出
        try:
            with open("output.txt", "r") as f:
                line = f.readline().strip()
                if line == "PASS":
                    action = "PASS"
                    x, y = -1, -1
                else:
                    x, y = map(int, line.split(","))
                    action = "MOVE"
        except:
            print("读取 output.txt 失败，游戏结束")
            winner = 2 if piece_type == 1 else 1
            print(f"Player {piece_type} 出错，Player {winner} 获胜")
            return

        # 读取棋盘
        piece_type_file, prev_board, curr_board = readInput(size)
        go = GO(size)
        go.set_board(piece_type, prev_board, curr_board)

        # 执行落子
        valid = True
        if action != "PASS":
            valid = go.place_chess(x, y, piece_type)
            if valid:
                go.died_pieces = go.remove_died_pieces(3 - piece_type)
            else:
                print(f"非法落子 ({x},{y})，Player {piece_type} 失败")
                winner = 2 if piece_type == 1 else 1
                print(f"Player {winner} 获胜")
                return
            consecutive_passes = 0
        else:
            go.previous_board = go.board
            consecutive_passes += 1

        if verbose:
            print_board(go.board)

        # 判断游戏结束
        if go.game_end(piece_type, action) or consecutive_passes >= 2:
            winner = go.judge_winner()
            print("\n游戏结束！")
            if winner == 0:
                print("平局！")
            else:
                print(f"Player {winner} 获胜 ({'X' if winner==1 else 'O'})")
            return

        # 写回 input.txt 给下一位玩家
        next_piece_type = 2 if piece_type == 1 else 1
        writeNextInput(next_piece_type, go.previous_board, go.board)

        piece_type = next_piece_type
        moves += 1

if __name__ == "__main__":
    main()
