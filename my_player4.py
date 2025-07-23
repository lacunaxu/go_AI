import random
import numpy as np
from read import readInput
from write import writeOutput

class GoGame:
    def __init__(self, board_size=5):
        self.BOARD_SIZE = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.prev_board = np.copy(self.board)

    def load_boards(self, color, prev_board, curr_board):
        self.color = color
        self.prev_board = np.array(prev_board, dtype=int)
        self.board = np.array(curr_board, dtype=int)

    def get_neighbors(self, row, col):
        directions = [(row-1,col), (row+1,col), (row,col-1), (row,col+1)]
        return [p for p in directions if 0 <= p[0] < self.BOARD_SIZE and 0 <= p[1] < self.BOARD_SIZE]

    def get_friendly_neighbors(self, board, row, col):
        return [p for p in self.get_neighbors(row, col) if board[p[0], p[1]] == board[row, col]]

    def get_friendly_group(self, board, row, col):
        queue = [(row, col)]
        group = set()
        while queue:
            node = queue.pop(0)
            group.add(node)
            for neighbor in self.get_friendly_neighbors(board, node[0], node[1]):
                if neighbor not in queue and neighbor not in group:
                    queue.append(neighbor)
        return list(group)

    def count_group_liberties(self, board, row, col):
        group = self.get_friendly_group(board, row, col)
        liberties = set()
        for point in group:
            for neighbor in self.get_neighbors(point[0], point[1]):
                if board[neighbor[0], neighbor[1]] == 0:
                    liberties.add(neighbor)
        return len(liberties)

    def get_captured_stones(self, board, color):
        captured = []
        visited = np.zeros_like(board, dtype=bool)
        for i, j in np.ndindex(self.BOARD_SIZE, self.BOARD_SIZE):
            if board[i, j] == color and not visited[i, j]:
                group = self.get_friendly_group(board, i, j)
                for x, y in group:
                    visited[x, y] = True
                if self.count_group_liberties(board, i, j) == 0:
                    captured.extend(group)
        return captured

    def clear_stones(self, board, stones):
        for x, y in stones:
            board[x, y] = 0
        return board

    def clear_captured_stones(self, board, color):
        captured = self.get_captured_stones(board, color)
        return self.clear_stones(board, captured) if captured else board

    def is_ko_violation(self, prev_board, board):
        return np.array_equal(prev_board, board)

    def is_legal_action(self, board, prev_board, player, i, j):
        if board[i, j] != 0:
            return False

        # 禁止堵眼
        if self.is_eye(board, i, j, player):
            return False

        next_board = np.copy(board)
        next_board[i, j] = player
        next_board = self.clear_captured_stones(next_board, 3 - player)

        if self.count_group_liberties(next_board, i, j) >= 1 and not self.is_ko_violation(prev_board, next_board):
            return True
        return False

    
    def is_eye(self, board, row, col, color):
        if board[row, col] != 0:
            return False
        neighbors = self.get_neighbors(row, col)
        for ni, nj in neighbors:
            if board[ni, nj] != color:
                return False
        return True

    def list_legal_moves(self, board, prev_board, player):
        legal = []
        for i, j in np.ndindex(self.BOARD_SIZE, self.BOARD_SIZE):
            if self.is_legal_action(board, prev_board, player, i, j):
                legal.append((i, j))
        return legal

    def simulate_move(self, board, move, player):
        new_board = np.copy(board)
        new_board[move[0], move[1]] = player
        new_board = self.clear_captured_stones(new_board, 3 - player)
        return new_board
    
    def territory_control_score(self, board, color):
        score = 0
        visited = set()

        for i, j in np.ndindex(self.BOARD_SIZE, self.BOARD_SIZE):
            if board[i, j] != 0 or (i, j) in visited:
                continue  # 非空位跳过

            # 搜索周围棋子，评估影响力
            influence = {color: 0, 3 - color: 0}

            for dx in range(-2, 3):  # 扫描5x5邻域
                for dy in range(-2, 3):
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < self.BOARD_SIZE and 0 <= nj < self.BOARD_SIZE:
                        dist = abs(dx) + abs(dy)
                        if board[ni, nj] in (color, 3 - color) and dist > 0:
                            weight = max(0, 3 - dist)  # 距离越近影响越大
                            liberties = self.count_group_liberties(board, ni, nj)
                            influence[board[ni, nj]] += weight + 0.3 * liberties  # 加权气数影响力

            # 判断控制归属
            if influence[color] > influence[3 - color]:
                control_sign = 1  # 我方控制
                control_strength = influence[color] - influence[3 - color]
            elif influence[color] < influence[3 - color]:
                control_sign = -1  # 敌方控制
                control_strength = influence[3 - color] - influence[color]
            else:
                control_sign = 0
                control_strength = 0

            # 边缘系数：边缘越大越易被偷
            edge_factor = 1.0
            if i == 0 or i == self.BOARD_SIZE - 1 or j == 0 or j == self.BOARD_SIZE - 1:
                edge_factor = 1.2  # 鼓励控制边缘
            elif i == 1 or i == self.BOARD_SIZE - 2 or j == 1 or j == self.BOARD_SIZE - 2:
                edge_factor = 1.1

            # 加分到总评分
            score += control_sign * control_strength * edge_factor

            visited.add((i, j))

        return score



    def evaluate_board_state(self, board, color):
        score_self, score_opponent = 0, 0
        for i, j in np.ndindex(self.BOARD_SIZE, self.BOARD_SIZE):
            if board[i, j] == color:
                liberties = self.count_group_liberties(board, i, j)
                score_self += 1 + liberties + 0.5
                if liberties == 1:
                    score_self -= 1
            elif board[i, j] == 3 - color:
                liberties = self.count_group_liberties(board, i, j)
                score_opponent += 1 + liberties
                if liberties == 1:
                    score_self += 1  # 奖励威胁敌人

        # 区域控制评分（权重0.5倍）
        territory_score = self.territory_control_score(board, color)
        total_score = score_self - score_opponent + 0.5 * territory_score
        return total_score


class MiniMaxAI:
    def __init__(self, game, depth=2):
        self.game = game
        self.depth = depth
        self.transposition_table = {}  # 分离val和moves缓存

    def board_to_key(self, board):
        return hash(board.tobytes()) 

    def minimax(self, curr, prev, depth, alpha, beta, color):
        board_key = (self.board_to_key(curr), depth, color)

        # 检查缓存走法
        if board_key in self.transposition_table and 'moves' in self.transposition_table[board_key]:
            return self.transposition_table[board_key]['moves']

        best_val = -float('inf')
        best_moves = []
        valid_moves = self.game.list_legal_moves(curr, prev, color)

        for move in valid_moves:
            next_board = self.game.simulate_move(curr, move, color)
            val = -self.min_play(next_board, curr, depth - 1, -beta, -alpha, 3 - color)

            if val > best_val:
                best_val = val
                best_moves = [move]
                alpha = max(alpha, val)
            elif val == best_val:
                best_moves.append(move)

            if alpha >= beta:
                break

        # 缓存best_moves
        self.transposition_table[board_key] = {'val': best_val, 'moves': best_moves}
        return best_moves

    def min_play(self, curr, prev, depth, alpha, beta, color):
        board_key = (self.board_to_key(curr), depth, color)

        # 检查缓存val
        if board_key in self.transposition_table and 'val' in self.transposition_table[board_key]:
            return self.transposition_table[board_key]['val']

        if depth == 0:
            val = self.game.evaluate_board_state(curr, self.game.color)
            self.transposition_table[board_key] = {'val': val}
            return val

        val = float('inf')
        valid_moves = self.game.list_legal_moves(curr, prev, color)

        for move in valid_moves:
            next_board = self.game.simulate_move(curr, move, color)
            val = min(val, -self.max_play(next_board, curr, depth - 1, -beta, -alpha, 3 - color))

            if val <= alpha:
                break
            beta = min(beta, val)

        self.transposition_table[board_key] = {'val': val}
        return val

    def max_play(self, curr, prev, depth, alpha, beta, color):
        board_key = (self.board_to_key(curr), depth, color)

        # 检查缓存val
        if board_key in self.transposition_table and 'val' in self.transposition_table[board_key]:
            return self.transposition_table[board_key]['val']

        if depth == 0:
            val = self.game.evaluate_board_state(curr, self.game.color)
            self.transposition_table[board_key] = {'val': val}
            return val

        val = -float('inf')
        valid_moves = self.game.list_legal_moves(curr, prev, color)

        for move in valid_moves:
            next_board = self.game.simulate_move(curr, move, color)
            val = max(val, -self.min_play(next_board, curr, depth - 1, -beta, -alpha, 3 - color))

            if val >= beta:
                break
            alpha = max(alpha, val)

        self.transposition_table[board_key] = {'val': val}
        return val

    def choose_best_move(self):
        # 检查双方是否均无棋可下（=局势已定）
        my_moves = self.game.list_legal_moves(self.game.board, self.game.prev_board, self.game.color)
        opp_moves = self.game.list_legal_moves(self.game.board, self.game.prev_board, 3 - self.game.color)

        if not my_moves and not opp_moves:
            return "PASS"  # 无需再下，局势已定，终局

        # 检查我能否下棋，否则 PASS
        if not my_moves:
            return "PASS"

        # 否则继续原先逻辑
        moves = self.minimax(self.game.board, self.game.prev_board, self.depth, -1000, 1000, self.game.color)
        return random.choice(moves) if moves else "PASS"


if __name__ == '__main__':
    color, prev_board, curr_board = readInput(5)

    game = GoGame()
    game.load_boards(color, prev_board, curr_board)
    ai = MiniMaxAI(game, depth=2)  # 你可以改成3测试稳定性
    action = ai.choose_best_move()
    writeOutput(action)
