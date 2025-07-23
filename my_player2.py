import copy
import random
import time
from read import readInput
from write import writeOutput

BOARD_SIZE = 5

class GoGame:
    def __init__(self, board, prev_board, piece_type):
        self.size = BOARD_SIZE
        self.board = board
        self.prev_board = prev_board
        self.piece_type = piece_type
        self.DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def get_neighbors(self, i, j):
        return [(i + dx, j + dy) for dx, dy in self.DIRECTIONS if 0 <= i + dx < self.size and 0 <= j + dy < self.size]

    def find_cluster(self, board, row, col):
        color = board[row][col]
        stack = [(row, col)]
        cluster = set()
        while stack:
            x, y = stack.pop()
            if (x, y) not in cluster:
                cluster.add((x, y))
                for nx, ny in self.get_neighbors(x, y):
                    if board[nx][ny] == color:
                        stack.append((nx, ny))
        return cluster

    def has_liberty(self, board, cluster):
        for x, y in cluster:
            for nx, ny in self.get_neighbors(x, y):
                if board[nx][ny] == 0:
                    return True
        return False

    def remove_dead_stones(self, board, color):
        new_board = [row[:] for row in board]
        for i in range(self.size):
            for j in range(self.size):
                if new_board[i][j] == color:
                    cluster = self.find_cluster(new_board, i, j)
                    if not self.has_liberty(new_board, cluster):
                        for x, y in cluster:
                            new_board[x][y] = 0
        return new_board

    def is_valid_move(self, board, prev_board, x, y, color):
        if board[x][y] != 0:
            return False
        new_board = [row[:] for row in board]
        new_board[x][y] = color
        new_board = self.remove_dead_stones(new_board, 3 - color)
        cluster = self.find_cluster(new_board, x, y)
        if not self.has_liberty(new_board, cluster):
            return False
        if new_board == prev_board:
            return False
        return True

    def get_legal_moves(self):
        moves = [(i, j) for i in range(self.size) for j in range(self.size)
                 if self.is_valid_move(self.board, self.prev_board, i, j, self.piece_type)]
        return moves if moves else ["PASS"]

    def do_move(self, move):
        new_board = [row[:] for row in self.board]
        if move == "PASS":
            return GoGame(new_board, self.board, 3 - self.piece_type)
        i, j = move
        new_board[i][j] = self.piece_type
        new_board = self.remove_dead_stones(new_board, 3 - self.piece_type)
        return GoGame(new_board, self.board, 3 - self.piece_type)

    def evaluate(self, player):
        black, white = 0, 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 1:
                    black += 1
                elif self.board[i][j] == 2:
                    white += 1
        score = black - white
        return score if player == 1 else -score

class MCTS:
    def __init__(self):
        pass

    def get_best_move(self, state):
        start_time = time.time()
        legal_moves = state.get_legal_moves()

        if legal_moves == ["PASS"]:
            return "PASS"

        move_scores = {move: 0 for move in legal_moves}
        move_counts = {move: 0 for move in legal_moves}

        move_index = 0
        num_moves = len(legal_moves)

        while time.time() - start_time < 0.9:
            move = legal_moves[move_index]
            next_state = state.do_move(move)
            result = self.simulate(next_state, state.piece_type)
            move_scores[move] += result
            move_counts[move] += 1

            move_index = (move_index + 1) % num_moves  
            
        best_move = max(move_scores.items(), key=lambda x: x[1] / move_counts[x[0]])[0]
        return best_move

    def simulate(self, state, player):
        curr_state = state
        for _ in range(5):
            legal_moves = curr_state.get_legal_moves()
            if legal_moves == ["PASS"]:
                break
            move = random.choice(legal_moves)
            curr_state = curr_state.do_move(move)
        return curr_state.evaluate(player)


if __name__ == '__main__':
    piece_type, prev_board, curr_board = readInput(BOARD_SIZE)
    state = GoGame(curr_board, prev_board, piece_type)
    agent = MCTS()
    move = agent.get_best_move(state)
    writeOutput(move)
